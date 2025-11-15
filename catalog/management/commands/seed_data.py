from django.core.management.base import BaseCommand
from catalog.models import Media, Genre
from django.utils import timezone
from datetime import date

class Command(BaseCommand):
    help = 'Cria dados de exemplo para demonstração (sem API do TMDB)'

    def handle(self, *args, **options):
        self.stdout.write('🎬 Criando dados de exemplo...')
        
        # Criar gêneros
        genres_data = [
            {'name': 'Ação', 'tmdb_id': 28},
            {'name': 'Aventura', 'tmdb_id': 12},
            {'name': 'Animação', 'tmdb_id': 16},
            {'name': 'Comédia', 'tmdb_id': 35},
            {'name': 'Crime', 'tmdb_id': 80},
            {'name': 'Documentário', 'tmdb_id': 99},
            {'name': 'Drama', 'tmdb_id': 18},
            {'name': 'Família', 'tmdb_id': 10751},
            {'name': 'Fantasia', 'tmdb_id': 14},
            {'name': 'Ficção Científica', 'tmdb_id': 878},
            {'name': 'Terror', 'tmdb_id': 27},
            {'name': 'Thriller', 'tmdb_id': 53},
            {'name': 'Romance', 'tmdb_id': 10749},
        ]
        
        for genre_data in genres_data:
            genre, created = Genre.objects.get_or_create(
                tmdb_id=genre_data['tmdb_id'],
                defaults={'name': genre_data['name']}
            )
            if created:
                self.stdout.write(f'   ✅ Gênero criado: {genre.name}')
        
        # Criar filmes de exemplo
        movies_data = [
            {
                'title': 'Top Gun: Maverick',
                'overview': 'Depois de mais de 30 anos de serviço como um dos principais aviadores da Marinha, Pete "Maverick" Mitchell está onde deveria estar, empurrando os limites como um piloto de testes corajoso.',
                'release_date': date(2022, 5, 27),
                'runtime': 130,
                'vote_average': 8.3,
                'poster_path': '/62HCnUTziyWcpDaBO2i1DX17ljH.jpg',
                'backdrop_path': '/odJ4hx6g6vBt4lBWKFD1tI8WS4x.jpg',
                'genres': ['Ação', 'Drama']
            },
            {
                'title': 'Avatar: O Caminho da Água',
                'overview': 'Ambientado mais de uma década após os eventos do primeiro filme, Avatar: O Caminho da Água começa a contar a história da família Sully.',
                'release_date': date(2022, 12, 16),
                'runtime': 192,
                'vote_average': 7.6,
                'poster_path': '/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg',
                'backdrop_path': '/s16H6tpK2utvwDtzZ8Qy4qm5Emw.jpg',
                'genres': ['Ficção Científica', 'Aventura', 'Ação']
            },
            {
                'title': 'Homem-Aranha: Sem Volta Para Casa',
                'overview': 'Peter Parker é desmascarado e não consegue mais separar sua vida normal dos grandes riscos de ser um super-herói.',
                'release_date': date(2021, 12, 17),
                'runtime': 148,
                'vote_average': 8.4,
                'poster_path': '/1g0dhYtq4irTY1GPXvft6k4YLjm.jpg',
                'backdrop_path': '/14QbnygCuTO0vl7CAFmPf1fgZfV.jpg',
                'genres': ['Ação', 'Aventura', 'Ficção Científica']
            },
            {
                'title': 'Vingadores: Ultimato',
                'overview': 'Após os eventos devastadores de Vingadores: Guerra Infinita, o universo está em ruínas devido aos esforços do Titã Louco, Thanos.',
                'release_date': date(2019, 4, 26),
                'runtime': 181,
                'vote_average': 8.3,
                'poster_path': '/or06FN3Dka5tukK1e9sl16pB3iy.jpg',
                'backdrop_path': '/7RyHsO4yDXtBv1zUU3mTpHeQ0d5.jpg',
                'genres': ['Aventura', 'Ficção Científica', 'Ação']
            },
            {
                'title': 'Parasita',
                'overview': 'A família Kim vive em um porão mal-cheiroso e luta para conseguir um trabalho. Quando o filho consegue um emprego como professor particular, uma oportunidade surge.',
                'release_date': date(2019, 5, 30),
                'runtime': 132,
                'vote_average': 8.5,
                'poster_path': '/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg',
                'backdrop_path': '/TU9NIjwzjoKPwQHoHshkFcQUCG.jpg',
                'genres': ['Thriller', 'Drama', 'Comédia']
            }
        ]
        
        # Criar séries de exemplo
        tv_shows_data = [
            {
                'title': 'House of the Dragon',
                'overview': 'A guerra civil da família Targaryen acontece 200 anos antes dos eventos de Game of Thrones.',
                'release_date': date(2022, 8, 21),
                'number_of_seasons': 1,
                'number_of_episodes': 10,
                'vote_average': 8.5,
                'poster_path': '/z2yahl2uefxDCl0nogcRBstwruJ.jpg',
                'backdrop_path': '/1X4h40fcB4WWUmIBK0auT4DKWWN.jpg',
                'genres': ['Drama', 'Fantasia', 'Ação']
            },
            {
                'title': 'Stranger Things',
                'overview': 'Quando um garoto desaparece, uma cidade enfrenta terrores sobrenaturais.',
                'release_date': date(2016, 7, 15),
                'number_of_seasons': 4,
                'number_of_episodes': 42,
                'vote_average': 8.7,
                'poster_path': '/49WJfeN0moxb9IPfGn8AIqMGskD.jpg',
                'backdrop_path': '/56v2KjBlU4XaOv9rVYEQypROD7P.jpg',
                'genres': ['Drama', 'Fantasia', 'Terror']
            },
            {
                'title': 'The Witcher',
                'overview': 'Geralt de Rivia é um bruxo solitário que luta para encontrar seu lugar em um mundo onde as pessoas são mais perversas que os monstros.',
                'release_date': date(2019, 12, 20),
                'number_of_seasons': 3,
                'number_of_episodes': 24,
                'vote_average': 8.2,
                'poster_path': '/cZ0d3rtvXPVvuiX22sP79K3Hmjz.jpg',
                'backdrop_path': '/1qpUk27LVI9UoTS7S0EixUBj5aR.jpg',
                'genres': ['Ação', 'Aventura', 'Drama', 'Fantasia']
            },
            {
                'title': 'Wednesday',
                'overview': 'Wednesday Addams investiga uma onda de assassinatos que aterroriza a Academia Nevermore.',
                'release_date': date(2022, 11, 23),
                'number_of_seasons': 1,
                'number_of_episodes': 8,
                'vote_average': 8.5,
                'poster_path': '/9PFonBhy4cQy7Jz20NpMygczOkv.jpg',
                'backdrop_path': '/iHSwvRVsRyxpX7FE7GbviaDvgGZ.jpg',
                'genres': ['Comédia', 'Crime', 'Fantasia']
            },
            {
                'title': 'Breaking Bad',
                'overview': 'Um professor de química do ensino médio descobre que tem câncer terminal e se associa a um ex-aluno para produzir e vender metanfetamina.',
                'release_date': date(2008, 1, 20),
                'number_of_seasons': 5,
                'number_of_episodes': 62,
                'vote_average': 9.5,
                'poster_path': '/ggFHVNu6YYI5L9pCfOacjizRGt.jpg',
                'backdrop_path': '/tsRy63Mu5cu8etL1X7ZLyf7UP1M.jpg',
                'genres': ['Crime', 'Drama', 'Thriller']
            }
        ]
        
        movies_created = 0
        tv_shows_created = 0
        
        # Criar filmes
        for i, movie_data in enumerate(movies_data):
            media, created = Media.objects.get_or_create(
                tmdb_id=1000 + i,  # IDs fictícios
                media_type='movie',
                defaults={
                    'title': movie_data['title'],
                    'overview': movie_data['overview'],
                    'release_date': movie_data['release_date'],
                    'runtime': movie_data['runtime'],
                    'vote_average': movie_data['vote_average'],
                    'poster_path': movie_data['poster_path'],
                    'backdrop_path': movie_data['backdrop_path'],
                    'popularity': movie_data['vote_average'] * 100,
                    'vote_count': 1000
                }
            )
            
            if created:
                # Adicionar gêneros
                for genre_name in movie_data['genres']:
                    try:
                        genre = Genre.objects.get(name=genre_name)
                        media.genres.add(genre)
                    except Genre.DoesNotExist:
                        pass
                
                movies_created += 1
                self.stdout.write(f'   ✅ Filme criado: {media.title}')
        
        # Criar séries
        for i, tv_data in enumerate(tv_shows_data):
            media, created = Media.objects.get_or_create(
                tmdb_id=2000 + i,  # IDs fictícios
                media_type='tv',
                defaults={
                    'title': tv_data['title'],
                    'overview': tv_data['overview'],
                    'release_date': tv_data['release_date'],
                    'number_of_seasons': tv_data['number_of_seasons'],
                    'number_of_episodes': tv_data['number_of_episodes'],
                    'vote_average': tv_data['vote_average'],
                    'poster_path': tv_data['poster_path'],
                    'backdrop_path': tv_data['backdrop_path'],
                    'popularity': tv_data['vote_average'] * 100,
                    'vote_count': 1000
                }
            )
            
            if created:
                # Adicionar gêneros
                for genre_name in tv_data['genres']:
                    try:
                        genre = Genre.objects.get(name=genre_name)
                        media.genres.add(genre)
                    except Genre.DoesNotExist:
                        pass
                
                tv_shows_created += 1
                self.stdout.write(f'   ✅ Série criada: {media.title}')
        
        # Resumo
        self.stdout.write('\n📊 RESUMO:')
        self.stdout.write(f'🎬 Gêneros: {Genre.objects.count()}')
        self.stdout.write(f'🎥 Filmes criados: {movies_created}')
        self.stdout.write(f'📺 Séries criadas: {tv_shows_created}')
        self.stdout.write(f'📈 Total de mídias: {Media.objects.count()}')
        self.stdout.write('\n✨ Dados de exemplo criados com sucesso!')