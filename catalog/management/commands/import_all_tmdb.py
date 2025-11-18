import time
from django.core.management.base import BaseCommand
from catalog.models import Media, Genre, Cast, Crew
from services.tmdb_service import tmdb_service


class Command(BaseCommand):
    help = 'Importa uma grande quantidade de filmes e séries da TMDB API'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--movies-pages',
            type=int,
            default=50,
            help='Número de páginas de filmes para importar (default: 50 = ~1000 filmes)'
        )
        parser.add_argument(
            '--tv-pages',
            type=int,
            default=30,
            help='Número de páginas de séries para importar (default: 30 = ~600 séries)'
        )
        parser.add_argument(
            '--include-details',
            action='store_true',
            help='Incluir detalhes completos (cast, crew) - mais lento mas completo'
        )
    
    def handle(self, *args, **options):
        movies_pages = options['movies_pages']
        tv_pages = options['tv_pages']
        include_details = options['include_details']
        
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando importação massiva da TMDB API...'))
        
        # Importar gêneros primeiro
        self.import_genres()
        
        # Importar filmes populares
        self.stdout.write(self.style.SUCCESS(f'🎬 Importando {movies_pages} páginas de filmes...'))
        self.import_popular_movies(movies_pages, include_details)
        
        # Importar séries populares
        self.stdout.write(self.style.SUCCESS(f'📺 Importando {tv_pages} páginas de séries...'))
        self.import_popular_tv_shows(tv_pages, include_details)
        
        # Importar filmes em cartaz
        self.stdout.write(self.style.SUCCESS('🎭 Importando filmes em cartaz...'))
        self.import_now_playing_movies(5, include_details)
        
        # Importar filmes bem avaliados
        self.stdout.write(self.style.SUCCESS('⭐ Importando filmes bem avaliados...'))
        self.import_top_rated_movies(10, include_details)
        
        self.stdout.write(self.style.SUCCESS('✅ Importação concluída!'))
        self.show_final_stats()
    
    def import_genres(self):
        """Importar todos os gêneros"""
        self.stdout.write('🏷️ Importando gêneros...')
        
        # Gêneros de filmes
        movie_genres = tmdb_service.get_movie_genres()
        if movie_genres:
            for genre_data in movie_genres:
                Genre.objects.get_or_create(
                    tmdb_id=genre_data['id'],
                    defaults={'name': genre_data['name']}
                )
        
        # Gêneros de TV
        tv_genres = tmdb_service.get_tv_genres()
        if tv_genres:
            for genre_data in tv_genres:
                Genre.objects.get_or_create(
                    tmdb_id=genre_data['id'],
                    defaults={'name': genre_data['name']}
                )
        
        self.stdout.write(f'✅ Gêneros importados: {Genre.objects.count()}')
    
    def import_popular_movies(self, pages, include_details):
        """Importar filmes populares"""
        imported = 0
        
        for page in range(1, pages + 1):
            self.stdout.write(f'📄 Página {page}/{pages} de filmes populares...')
            
            response = tmdb_service.get_popular_movies(page=page)
            if not response or 'results' not in response:
                continue
                
            movies = response['results']
            for movie_data in movies:
                try:
                    movie, created = self.create_or_update_media(movie_data, 'movie', include_details)
                    if created:
                        imported += 1
                        if imported % 50 == 0:
                            self.stdout.write(f'📊 {imported} filmes importados...')
                    
                    # Pequena pausa para não sobrecarregar a API
                    time.sleep(0.1)
                    
                except Exception as e:
                    title = movie_data.get('title', 'unknown') if isinstance(movie_data, dict) else 'unknown'
                    self.stdout.write(f'❌ Erro ao importar filme {title}: {e}')
        
        self.stdout.write(f'🎬 Total de filmes populares importados: {imported}')
    
    def import_popular_tv_shows(self, pages, include_details):
        """Importar séries populares"""
        imported = 0
        
        for page in range(1, pages + 1):
            self.stdout.write(f'📄 Página {page}/{pages} de séries populares...')
            
            response = tmdb_service.get_popular_tv(page=page)
            if not response or 'results' not in response:
                continue
                
            tv_shows = response['results']
            for tv_data in tv_shows:
                try:
                    tv_show, created = self.create_or_update_media(tv_data, 'tv', include_details)
                    if created:
                        imported += 1
                        if imported % 30 == 0:
                            self.stdout.write(f'📊 {imported} séries importadas...')
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    name = tv_data.get('name', 'unknown') if isinstance(tv_data, dict) else 'unknown'
                    self.stdout.write(f'❌ Erro ao importar série {name}: {e}')
        
        self.stdout.write(f'📺 Total de séries populares importadas: {imported}')
    
    def import_now_playing_movies(self, pages, include_details):
        """Importar filmes em cartaz"""
        imported = 0
        
        for page in range(1, pages + 1):
            movies = tmdb_service.get_now_playing_movies(page=page)
            if not movies:
                continue
                
            for movie_data in movies:
                try:
                    movie, created = self.create_or_update_media(movie_data, 'movie', include_details)
                    if created:
                        imported += 1
                    time.sleep(0.1)
                except Exception as e:
                    continue
        
        self.stdout.write(f'🎭 Filmes em cartaz importados: {imported}')
    
    def import_top_rated_movies(self, pages, include_details):
        """Importar filmes bem avaliados"""
        imported = 0
        
        for page in range(1, pages + 1):
            movies = tmdb_service.get_top_rated_movies(page=page)
            if not movies:
                continue
                
            for movie_data in movies:
                try:
                    movie, created = self.create_or_update_media(movie_data, 'movie', include_details)
                    if created:
                        imported += 1
                    time.sleep(0.1)
                except Exception as e:
                    continue
        
        self.stdout.write(f'⭐ Filmes bem avaliados importados: {imported}')
    
    def create_or_update_media(self, data, media_type, include_details=True):
        """Criar ou atualizar mídia com dados completos"""
        tmdb_id = data.get('id')
        
        if not tmdb_id:
            return None, False
        
        # Verificar se já existe
        media, created = Media.objects.get_or_create(
            tmdb_id=tmdb_id,
            defaults=self.extract_media_data(data, media_type)
        )
        
        if created:
            # Associar gêneros
            genre_ids = data.get('genre_ids', [])
            if genre_ids:
                genres = Genre.objects.filter(tmdb_id__in=genre_ids)
                media.genres.set(genres)
            
            # Importar detalhes completos se solicitado
            if include_details:
                self.import_media_details(media, tmdb_id, media_type)
        
        return media, created
    
    def extract_media_data(self, data, media_type):
        """Extrair dados básicos da mídia"""
        if media_type == 'movie':
            title = data.get('title', '')
            original_title = data.get('original_title', '')
            release_date = data.get('release_date', None)
        else:  # tv
            title = data.get('name', '')
            original_title = data.get('original_name', '')
            release_date = data.get('first_air_date', None)
        
        # Converter data
        if release_date:
            try:
                from datetime import datetime
                release_date = datetime.strptime(release_date, '%Y-%m-%d').date()
            except:
                release_date = None
        
        return {
            'title': title,
            'original_title': original_title,
            'overview': data.get('overview', ''),
            'release_date': release_date,
            'poster_path': data.get('poster_path', ''),
            'backdrop_path': data.get('backdrop_path', ''),
            'media_type': media_type,
            'vote_average': data.get('vote_average', 0),
            'vote_count': data.get('vote_count', 0),
            'popularity': data.get('popularity', 0),
            'original_language': data.get('original_language', ''),
        }
    
    def import_media_details(self, media, tmdb_id, media_type):
        """Importar detalhes completos (cast, crew, etc)"""
        try:
            if media_type == 'movie':
                details = tmdb_service.get_movie_details(tmdb_id)
                credits = tmdb_service.get_movie_credits(tmdb_id)
            else:
                details = tmdb_service.get_tv_details(tmdb_id)
                credits = tmdb_service.get_tv_credits(tmdb_id)
            
            if details:
                # Atualizar informações extras
                media.runtime = details.get('runtime') or details.get('episode_run_time', [None])[0]
                if media_type == 'tv':
                    media.number_of_seasons = details.get('number_of_seasons')
                    media.number_of_episodes = details.get('number_of_episodes')
                media.save()
            
            if credits:
                # Importar cast
                cast_data = credits.get('cast', [])
                for person in cast_data[:10]:  # Primeiros 10 atores
                    Cast.objects.get_or_create(
                        media=media,
                        tmdb_person_id=person.get('id'),
                        defaults={
                            'name': person.get('name', ''),
                            'character': person.get('character', ''),
                            'profile_path': person.get('profile_path', ''),
                            'order': person.get('order', 999)
                        }
                    )
                
                # Importar crew principais (diretor, roteirista, etc)
                crew_data = credits.get('crew', [])
                important_jobs = ['Director', 'Writer', 'Producer', 'Executive Producer']
                for person in crew_data:
                    if person.get('job') in important_jobs:
                        Crew.objects.get_or_create(
                            media=media,
                            tmdb_person_id=person.get('id'),
                            job=person.get('job', ''),
                            defaults={
                                'name': person.get('name', ''),
                                'department': person.get('department', ''),
                                'profile_path': person.get('profile_path', '')
                            }
                        )
        
        except Exception as e:
            self.stdout.write(f'⚠️ Erro ao importar detalhes: {e}')
    
    def show_final_stats(self):
        """Mostrar estatísticas finais"""
        total_movies = Media.objects.filter(media_type='movie').count()
        total_tv = Media.objects.filter(media_type='tv').count()
        total_genres = Genre.objects.count()
        total_cast = Cast.objects.count()
        total_crew = Crew.objects.count()
        
        self.stdout.write(self.style.SUCCESS('\n📊 ESTATÍSTICAS FINAIS:'))
        self.stdout.write(f'🎬 Filmes: {total_movies}')
        self.stdout.write(f'📺 Séries: {total_tv}')
        self.stdout.write(f'🏷️ Gêneros: {total_genres}')
        self.stdout.write(f'🎭 Atores: {total_cast}')
        self.stdout.write(f'🎥 Equipe Técnica: {total_crew}')
        self.stdout.write(f'🎯 Total de Mídia: {total_movies + total_tv}')