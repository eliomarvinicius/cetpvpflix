import requests
from django.conf import settings
from catalog.models import Media, Genre, Cast, Crew
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class TMDBService:
    """
    Serviço para integração com The Movie Database (TMDB) API
    """
    
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.image_base_url = settings.TMDB_IMAGE_BASE_URL
        self.session = requests.Session()
        self.session.params.update({'api_key': self.api_key, 'language': 'pt-BR'})
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Faz requisição para a API do TMDB
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição TMDB: {e}")
            return None
    
    def search_multi(self, query: str, page: int = 1) -> Optional[Dict]:
        """
        Busca por filmes e séries
        """
        return self._make_request('search/multi', {'query': query, 'page': page})
    
    def get_popular_movies(self, page: int = 1) -> Optional[Dict]:
        """
        Obtém filmes populares
        """
        return self._make_request('movie/popular', {'page': page})
    
    def get_popular_tv(self, page: int = 1) -> Optional[Dict]:
        """
        Obtém séries populares
        """
        return self._make_request('tv/popular', {'page': page})
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """
        Obtém detalhes de um filme
        """
        return self._make_request(f'movie/{movie_id}', {
            'append_to_response': 'credits,videos,similar,reviews'
        })
    
    def get_tv_details(self, tv_id: int) -> Optional[Dict]:
        """
        Obtém detalhes de uma série
        """
        return self._make_request(f'tv/{tv_id}', {
            'append_to_response': 'credits,videos,similar,reviews'
        })
    
    def get_genres(self, media_type: str = 'movie') -> Optional[Dict]:
        """
        Obtém lista de gêneros
        """
        return self._make_request(f'genre/{media_type}/list')
    
    def import_genres(self):
        """
        Importa gêneros do TMDB para o banco local
        """
        # Importar gêneros de filmes
        movie_genres = self.get_genres('movie')
        if movie_genres:
            for genre_data in movie_genres.get('genres', []):
                Genre.objects.get_or_create(
                    tmdb_id=genre_data['id'],
                    defaults={'name': genre_data['name']}
                )
        
        # Importar gêneros de TV
        tv_genres = self.get_genres('tv')
        if tv_genres:
            for genre_data in tv_genres.get('genres', []):
                Genre.objects.get_or_create(
                    tmdb_id=genre_data['id'],
                    defaults={'name': genre_data['name']}
                )
    
    def create_or_update_media(self, tmdb_data: Dict, media_type: str) -> Optional[Media]:
        """
        Cria ou atualiza um objeto Media com dados do TMDB
        """
        try:
            media, created = Media.objects.get_or_create(
                tmdb_id=tmdb_data['id'],
                defaults={
                    'title': tmdb_data.get('title') or tmdb_data.get('name', ''),
                    'original_title': tmdb_data.get('original_title') or tmdb_data.get('original_name', ''),
                    'overview': tmdb_data.get('overview', ''),
                    'poster_path': tmdb_data.get('poster_path', ''),
                    'backdrop_path': tmdb_data.get('backdrop_path', ''),
                    'media_type': media_type,
                    'vote_average': tmdb_data.get('vote_average', 0),
                    'vote_count': tmdb_data.get('vote_count', 0),
                    'popularity': tmdb_data.get('popularity', 0),
                    'original_language': tmdb_data.get('original_language', ''),
                }
            )
            
            # Atualizar campos específicos baseados no tipo
            if media_type == 'movie':
                release_date = tmdb_data.get('release_date')
                if release_date:
                    from datetime import datetime
                    media.release_date = datetime.strptime(release_date, '%Y-%m-%d').date()
                media.runtime = tmdb_data.get('runtime')
            
            elif media_type == 'tv':
                first_air_date = tmdb_data.get('first_air_date')
                if first_air_date:
                    from datetime import datetime
                    media.release_date = datetime.strptime(first_air_date, '%Y-%m-%d').date()
                media.number_of_seasons = tmdb_data.get('number_of_seasons')
                media.number_of_episodes = tmdb_data.get('number_of_episodes')
            
            # Associar gêneros
            if 'genres' in tmdb_data:
                genre_ids = [g['id'] for g in tmdb_data['genres']]
                genres = Genre.objects.filter(tmdb_id__in=genre_ids)
                media.genres.set(genres)
            elif 'genre_ids' in tmdb_data:
                genres = Genre.objects.filter(tmdb_id__in=tmdb_data['genre_ids'])
                media.genres.set(genres)
            
            media.save()
            
            # Importar elenco se disponível
            if 'credits' in tmdb_data:
                self._import_credits(media, tmdb_data['credits'])
            
            return media
            
        except Exception as e:
            logger.error(f"Erro ao criar/atualizar media: {e}")
            return None
    
    def _import_credits(self, media: Media, credits_data: Dict):
        """
        Importa elenco e equipe técnica
        """
        # Limpar elenco existente
        media.cast_members.all().delete()
        media.crew_members.all().delete()
        
        # Importar elenco
        for cast_member in credits_data.get('cast', [])[:10]:  # Limitar a 10 principais
            Cast.objects.create(
                media=media,
                name=cast_member.get('name', ''),
                character=cast_member.get('character', ''),
                profile_path=cast_member.get('profile_path', ''),
                tmdb_person_id=cast_member.get('id'),
                order=cast_member.get('order', 0)
            )
        
        # Importar equipe técnica (diretor, roteirista, etc.)
        important_jobs = ['Director', 'Writer', 'Screenplay', 'Producer']
        for crew_member in credits_data.get('crew', []):
            if crew_member.get('job') in important_jobs:
                Crew.objects.create(
                    media=media,
                    name=crew_member.get('name', ''),
                    job=crew_member.get('job', ''),
                    department=crew_member.get('department', ''),
                    profile_path=crew_member.get('profile_path', ''),
                    tmdb_person_id=crew_member.get('id')
                )
    
    def populate_database(self, pages: int = 5):
        """
        Popula o banco com filmes e séries populares do TMDB
        """
        # Primeiro, importar gêneros
        self.import_genres()
        
        # Importar filmes populares
        for page in range(1, pages + 1):
            movies = self.get_popular_movies(page)
            if movies:
                for movie_data in movies.get('results', []):
                    # Buscar detalhes completos
                    details = self.get_movie_details(movie_data['id'])
                    if details:
                        self.create_or_update_media(details, 'movie')
        
        # Importar séries populares
        for page in range(1, pages + 1):
            tv_shows = self.get_popular_tv(page)
            if tv_shows:
                for tv_data in tv_shows.get('results', []):
                    # Buscar detalhes completos
                    details = self.get_tv_details(tv_data['id'])
                    if details:
                        self.create_or_update_media(details, 'tv')

# Instância global do serviço
tmdb_service = TMDBService()