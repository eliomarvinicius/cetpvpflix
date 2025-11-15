from django.core.management.base import BaseCommand
from django.conf import settings
from services.tmdb_service import TMDBService
from catalog.models import Media
import time

class Command(BaseCommand):
    help = 'Popula o banco de dados com filmes e séries populares do TMDB'

    def add_arguments(self, parser):
        parser.add_argument(
            '--movies',
            type=int,
            default=20,
            help='Número de filmes para carregar (padrão: 20)',
        )
        parser.add_argument(
            '--tv-shows',
            type=int,
            default=20,
            help='Número de séries para carregar (padrão: 20)',
        )
        parser.add_argument(
            '--pages',
            type=int,
            default=1,
            help='Número de páginas para carregar de cada tipo (padrão: 1)',
        )

    def handle(self, *args, **options):
        tmdb_service = TMDBService()
        
        movies_count = options['movies']
        tv_shows_count = options['tv_shows']
        pages = options['pages']
        
        self.stdout.write('🎬 Iniciando população do banco de dados...')
        self.stdout.write(f'📊 Meta: {movies_count} filmes e {tv_shows_count} séries')
        
        # Carregar filmes populares
        self.stdout.write('\n🎥 Carregando filmes populares...')
        movies_loaded = 0
        
        for page in range(1, pages + 1):
            try:
                movies = tmdb_service.get_popular_movies(page=page)
                for movie_data in movies.get('results', []):
                    if movies_loaded >= movies_count:
                        break
                    
                    # Verificar se já existe
                    if Media.objects.filter(tmdb_id=movie_data['id'], media_type='movie').exists():
                        self.stdout.write(f'   ⚠️  Filme já existe: {movie_data["title"]}')
                        continue
                    
                    try:
                        # Buscar detalhes completos
                        movie_details = tmdb_service.get_movie_details(movie_data['id'])
                        
                        # Criar/atualizar filme
                        media = tmdb_service.create_or_update_media(movie_details, 'movie')
                        
                        if media:
                            movies_loaded += 1
                            self.stdout.write(f'   ✅ Carregado: {media.title} ({media.release_date.year if media.release_date else "N/A"})')
                            
                            # Pausa para não sobrecarregar a API
                            time.sleep(0.1)
                        
                    except Exception as e:
                        self.stdout.write(f'   ❌ Erro ao carregar filme {movie_data["title"]}: {str(e)}')
                
                if movies_loaded >= movies_count:
                    break
                    
            except Exception as e:
                self.stdout.write(f'❌ Erro ao buscar página {page} de filmes: {str(e)}')
        
        # Carregar séries populares
        self.stdout.write('\n📺 Carregando séries populares...')
        tv_shows_loaded = 0
        
        for page in range(1, pages + 1):
            try:
                tv_shows = tmdb_service.get_popular_tv(page=page)
                for tv_data in tv_shows.get('results', []):
                    if tv_shows_loaded >= tv_shows_count:
                        break
                    
                    # Verificar se já existe
                    if Media.objects.filter(tmdb_id=tv_data['id'], media_type='tv').exists():
                        self.stdout.write(f'   ⚠️  Série já existe: {tv_data["name"]}')
                        continue
                    
                    try:
                        # Buscar detalhes completos
                        tv_details = tmdb_service.get_tv_details(tv_data['id'])
                        
                        # Criar/atualizar série
                        media = tmdb_service.create_or_update_media(tv_details, 'tv')
                        
                        if media:
                            tv_shows_loaded += 1
                            self.stdout.write(f'   ✅ Carregada: {media.title} ({media.release_date.year if media.release_date else "N/A"})')
                            
                            # Pausa para não sobrecarregar a API
                            time.sleep(0.1)
                        
                    except Exception as e:
                        self.stdout.write(f'   ❌ Erro ao carregar série {tv_data["name"]}: {str(e)}')
                
                if tv_shows_loaded >= tv_shows_count:
                    break
                    
            except Exception as e:
                self.stdout.write(f'❌ Erro ao buscar página {page} de séries: {str(e)}')
        
        # Resumo
        self.stdout.write('\n📊 RESUMO DA POPULAÇÃO:')
        self.stdout.write(f'🎥 Filmes carregados: {movies_loaded}')
        self.stdout.write(f'📺 Séries carregadas: {tv_shows_loaded}')
        
        total_media = Media.objects.count()
        total_movies = Media.objects.filter(media_type='movie').count()
        total_tv_shows = Media.objects.filter(media_type='tv').count()
        
        self.stdout.write(f'\n📈 TOTAL NO BANCO DE DADOS:')
        self.stdout.write(f'🎬 Total de mídias: {total_media}')
        self.stdout.write(f'🎥 Total de filmes: {total_movies}')
        self.stdout.write(f'📺 Total de séries: {total_tv_shows}')
        
        self.stdout.write('\n✨ População concluída!')