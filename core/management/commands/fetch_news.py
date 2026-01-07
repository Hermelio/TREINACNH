"""
Comando para buscar notícias sobre DETRAN e trânsito de diversos portais.
Usage: python manage.py fetch_news
"""
import feedparser
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from datetime import datetime
from core.models import NewsArticle
import time


class Command(BaseCommand):
    help = 'Busca notícias sobre DETRAN e trânsito via RSS feeds e web scraping'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Número máximo de notícias por fonte'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        
        self.stdout.write(self.style.SUCCESS('🔍 Iniciando busca de notícias...'))
        
        # RSS Feeds de portais brasileiros
        feeds = [
            {
                'name': 'G1 Carros',
                'url': 'https://g1.globo.com/rss/g1/carros/',
                'source': 'G1',
                'keywords': ['detran', 'habilitação', 'cnh', 'carteira', 'trânsito', 'multa']
            },
            {
                'name': 'UOL Carros',
                'url': 'https://rss.uol.com.br/feed/carros.xml',
                'source': 'UOL',
                'keywords': ['detran', 'habilitação', 'cnh', 'carteira', 'trânsito', 'multa']
            },
            {
                'name': 'R7 Carros',
                'url': 'https://noticias.r7.com/carros/feed.xml',
                'source': 'R7',
                'keywords': ['detran', 'habilitação', 'cnh', 'carteira', 'trânsito', 'multa']
            },
        ]
        
        total_added = 0
        total_skipped = 0
        
        for feed_info in feeds:
            self.stdout.write(f'\n📰 Buscando em {feed_info["name"]}...')
            
            try:
                added, skipped = self.fetch_from_feed(
                    feed_info['url'],
                    feed_info['source'],
                    feed_info['keywords'],
                    limit
                )
                total_added += added
                total_skipped += skipped
                
                self.stdout.write(
                    self.style.SUCCESS(f'   ✓ {added} novas notícias | {skipped} duplicadas')
                )
                
                # Pausa entre requisições
                time.sleep(2)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ✗ Erro ao buscar: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Concluído! {total_added} notícias adicionadas | {total_skipped} ignoradas')
        )

    def fetch_from_feed(self, feed_url, source, keywords, limit):
        """Busca notícias de um feed RSS"""
        added = 0
        skipped = 0
        
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:limit * 2]:  # Busca mais para filtrar
                # Verifica se a notícia contém palavras-chave relevantes
                title_lower = entry.title.lower()
                summary_lower = entry.get('summary', '').lower()
                
                is_relevant = any(
                    keyword in title_lower or keyword in summary_lower
                    for keyword in keywords
                )
                
                if not is_relevant:
                    continue
                
                # Verifica se já existe
                slug = slugify(entry.title)[:250]  # Limita tamanho do slug
                
                if NewsArticle.objects.filter(slug=slug).exists():
                    skipped += 1
                    continue
                
                # Extrai informações
                title = entry.title
                source_url = entry.link
                summary = entry.get('summary', '')[:500]  # Limita resumo
                
                # Tenta extrair imagem
                image_url = self.extract_image(entry, source_url)
                
                # Data de publicação
                published_date = self.parse_date(entry)
                
                # Categoriza automaticamente
                category = self.categorize_news(title, summary)
                
                # Cria a notícia
                try:
                    NewsArticle.objects.create(
                        title=title,
                        slug=slug,
                        source=source,
                        source_url=source_url,
                        image_url=image_url,
                        summary=self.clean_html(summary),
                        published_date=published_date,
                        category=category,
                        is_active=True,
                        is_featured=False
                    )
                    added += 1
                    
                    if added >= limit:
                        break
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'   ⚠ Erro ao salvar notícia: {str(e)}')
                    )
                    skipped += 1
            
        except Exception as e:
            raise Exception(f'Erro ao processar feed: {str(e)}')
        
        return added, skipped

    def extract_image(self, entry, source_url):
        """Extrai URL da imagem da notícia"""
        # Tenta pegar do feed
        if hasattr(entry, 'media_content') and entry.media_content:
            return entry.media_content[0].get('url', '')
        
        if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
            return entry.media_thumbnail[0].get('url', '')
        
        # Tenta fazer scraping da página
        try:
            response = requests.get(source_url, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Procura por meta tags Open Graph
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                return og_image['content']
            
            # Procura pela primeira imagem no artigo
            article_img = soup.find('article')
            if article_img:
                img = article_img.find('img')
                if img and img.get('src'):
                    return img['src']
        
        except Exception:
            pass
        
        return ''

    def parse_date(self, entry):
        """Converte data do feed para datetime"""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                dt = datetime(*entry.published_parsed[:6])
                return timezone.make_aware(dt)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                dt = datetime(*entry.updated_parsed[:6])
                return timezone.make_aware(dt)
        except Exception:
            pass
        
        return timezone.now()

    def categorize_news(self, title, summary):
        """Categoriza automaticamente a notícia"""
        text = (title + ' ' + summary).lower()
        
        if any(word in text for word in ['lei', 'legislação', 'norma', 'código', 'regulamento']):
            return 'legislacao'
        elif any(word in text for word in ['habilitação', 'cnh', 'carteira', 'primeira habilitação', 'renovação']):
            return 'habilitacao'
        elif any(word in text for word in ['multa', 'infração', 'ponto', 'suspensão']):
            return 'multas'
        elif any(word in text for word in ['tecnologia', 'app', 'aplicativo', 'digital', 'eletrônico']):
            return 'tecnologia'
        elif any(word in text for word in ['acidente', 'segurança', 'prevenção', 'conscientização']):
            return 'seguranca'
        
        return 'outros'

    def clean_html(self, text):
        """Remove tags HTML do texto"""
        soup = BeautifulSoup(text, 'html.parser')
        return soup.get_text().strip()
