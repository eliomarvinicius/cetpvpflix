import requests
import logging
from django.conf import settings
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class TMDBService:
    """
    Serviço para integração com a TMDB API
    """
    
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.image_base_url = settings.TMDB_IMAGE_BASE_URL
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Faz uma requisição para a TMDB API
        """
        if params is None:
            params = {}
            
        params['api_key'] = self.api_key
        params['language'] = 'pt-BR'
        
        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Erro na requisição TMDB: {e}")
            return None
    
    def get_popular_movies(self, page: int = 1) -> Optional[Dict]:
        """
        Busca filmes populares
        """
        return self._make_request('movie/popular', {'page': page})
    
    def get_popular_tv_shows(self, page: int = 1) -> Optional[Dict]:
        """
        Busca séries populares
        """
        return self._make_request('tv/popular', {'page': page})
    
    def get_top_rated_movies(self, page: int = 1) -> Optional[Dict]:
        """
        Busca filmes mais bem avaliados
        """
        return self._make_request('movie/top_rated', {'page': page})
    
    def get_top_rated_tv_shows(self, page: int = 1) -> Optional[Dict]:
        """
        Busca séries mais bem avaliadas
        """
        return self._make_request('tv/top_rated', {'page': page})
    
    def search_multi(self, query: str, page: int = 1) -> Optional[Dict]:
        """
        Busca por filmes e séries
        """
        return self._make_request('search/multi', {'query': query, 'page': page})
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """
        Busca detalhes de um filme
        """
        return self._make_request(f'movie/{movie_id}', {'append_to_response': 'credits,videos'})
    
    def get_tv_details(self, tv_id: int) -> Optional[Dict]:
        """
        Busca detalhes de uma série
        """
        return self._make_request(f'tv/{tv_id}', {'append_to_response': 'credits,videos'})
    
    def get_genres_movies(self) -> Optional[Dict]:
        """
        Busca gêneros de filmes
        """
        return self._make_request('genre/movie/list')
    
    def get_genres_tv(self) -> Optional[Dict]:
        """
        Busca gêneros de séries
        """
        return self._make_request('genre/tv/list')
    
    def discover_movies(self, **kwargs) -> Optional[Dict]:
        """
        Descobrir filmes com filtros
        """
        return self._make_request('discover/movie', kwargs)
    
    def discover_tv(self, **kwargs) -> Optional[Dict]:
        """
        Descobrir séries com filtros
        """
        return self._make_request('discover/tv', kwargs)
    
    def get_movie_recommendations(self, movie_id: int, page: int = 1) -> Optional[Dict]:
        """
        Busca recomendações de filmes
        """
        return self._make_request(f'movie/{movie_id}/recommendations', {'page': page})
    
    def get_tv_recommendations(self, tv_id: int, page: int = 1) -> Optional[Dict]:
        """
        Busca recomendações de séries
        """
        return self._make_request(f'tv/{tv_id}/recommendations', {'page': page})
    
    def get_full_poster_url(self, poster_path: str, size: str = 'w500') -> str:
        """
        Gera URL completa para poster
        """
        if not poster_path:
            return ''
        return f"{self.image_base_url}{size}{poster_path}"
    
    def get_full_backdrop_url(self, backdrop_path: str, size: str = 'w1280') -> str:
        """
        Gera URL completa para backdrop
        """
        if not backdrop_path:
            return ''
        return f"{self.image_base_url}{size}{backdrop_path}"

# Instância única do serviço
tmdb_service = TMDBService()