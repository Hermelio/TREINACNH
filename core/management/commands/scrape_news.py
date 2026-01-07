"""
Scraper avançado para portais de notícias brasileiros.
Busca notícias diretamente das páginas quando RSS não está disponível.
"""
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import NewsArticle
import time
import re


class Command(BaseCommand):
    help = 'Faz web scraping de notícias sobre DETRAN e trânsito de portais brasileiros'

    def add_arguments(self, parser):
        parser.add_argument(
            '--portal',
            type=str,
            choices=['g1', 'uol', 'folha', 'estadao', 'all'],
            default='all',
            help='Portal específico para buscar notícias'
        )

    def handle(self, *args, **options):
        portal = options['portal']
        
        self.stdout.write(self.style.SUCCESS('🕷️  Iniciando web scraping de notícias...'))
        
        scrapers = {
            'g1': self.scrape_g1_detran,
            'uol': self.scrape_uol_transito,
            'folha': self.scrape_folha_transito,
            'estadao': self.scrape_estadao_transito,
        }
        
        total_added = 0
        
        if portal == 'all':
            for portal_name, scraper_func in scrapers.items():
                self.stdout.write(f'\n🔍 Buscando em {portal_name.upper()}...')
                try:
                    added = scraper_func()
                    total_added += added
                    self.stdout.write(self.style.SUCCESS(f'   ✓ {added} notícias encontradas'))
                    time.sleep(3)  # Pausa entre portais
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'   ✗ Erro: {str(e)}'))
        else:
            scraper_func = scrapers.get(portal)
            if scraper_func:
                total_added = scraper_func()
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Concluído! {total_added} notícias adicionadas')
        )

    def scrape_g1_detran(self):
        """Scraping específico do G1 - busca DETRAN"""
        added = 0
        
        # URLs de busca do G1
        search_terms = ['detran', 'habilitacao+cnh', 'carteira+motorista']
        
        for term in search_terms:
            try:
                url = f'https://g1.globo.com/busca/?q={term}&order=recent'
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Encontra os artigos
                articles = soup.find_all('div', class_='widget--info')[:5]
                
                for article in articles:
                    try:
                        title_tag = article.find('a', class_='widget--info__title')
                        if not title_tag:
                            continue
                        
                        title = title_tag.get_text(strip=True)
                        link = title_tag.get('href', '')
                        
                        if not link or NewsArticle.objects.filter(source_url=link).exists():
                            continue
                        
                        # Extrai resumo
                        summary_tag = article.find('p', class_='widget--info__description')
                        summary = summary_tag.get_text(strip=True) if summary_tag else title[:200]
                        
                        # Extrai imagem
                        img_tag = article.find('img')
                        image_url = img_tag.get('src', '') if img_tag else ''
                        
                        slug = slugify(title)[:250]
                        
                        NewsArticle.objects.create(
                            title=title,
                            slug=slug,
                            source='G1',
                            source_url=link,
                            image_url=image_url,
                            summary=summary,
                            published_date=timezone.now() - timedelta(hours=added),
                            category=self.categorize(title + ' ' + summary),
                            is_active=True,
                            is_featured=False
                        )
                        added += 1
                        
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'   ⚠ Erro ao processar artigo: {str(e)}'))
                
                time.sleep(2)  # Pausa entre buscas
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ✗ Erro na busca "{term}": {str(e)}'))
        
        return added

    def scrape_uol_transito(self):
        """Scraping do UOL - seção de trânsito"""
        added = 0
        
        try:
            url = 'https://www.uol.com.br/carros/transito/'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Encontra artigos
            articles = soup.find_all('h3', class_='titulo')[:10]
            
            for article in articles:
                try:
                    link_tag = article.find('a')
                    if not link_tag:
                        continue
                    
                    title = link_tag.get_text(strip=True)
                    link = link_tag.get('href', '')
                    
                    # Verifica relevância
                    if not any(word in title.lower() for word in ['detran', 'cnh', 'habilitação', 'multa', 'infração']):
                        continue
                    
                    if NewsArticle.objects.filter(source_url=link).exists():
                        continue
                    
                    slug = slugify(title)[:250]
                    
                    # Busca mais detalhes da notícia
                    details = self.fetch_article_details(link)
                    
                    NewsArticle.objects.create(
                        title=title,
                        slug=slug,
                        source='UOL',
                        source_url=link,
                        image_url=details.get('image', ''),
                        summary=details.get('summary', title[:200]),
                        published_date=timezone.now() - timedelta(hours=added),
                        category=self.categorize(title),
                        is_active=True,
                        is_featured=False
                    )
                    added += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'   ⚠ Erro ao processar: {str(e)}'))
        
        except Exception as e:
            raise Exception(f'Erro no scraping UOL: {str(e)}')
        
        return added

    def scrape_folha_transito(self):
        """Scraping da Folha - seção de cotidiano/trânsito"""
        added = 0
        
        try:
            url = 'https://www1.folha.uol.com.br/cotidiano/transito/'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('div', class_='c-headline')[:8]
            
            for article in articles:
                try:
                    link_tag = article.find('a')
                    if not link_tag:
                        continue
                    
                    title = link_tag.get_text(strip=True)
                    link = link_tag.get('href', '')
                    
                    if not link.startswith('http'):
                        link = 'https://www1.folha.uol.com.br' + link
                    
                    if NewsArticle.objects.filter(source_url=link).exists():
                        continue
                    
                    slug = slugify(title)[:250]
                    
                    NewsArticle.objects.create(
                        title=title,
                        slug=slug,
                        source='Folha de S.Paulo',
                        source_url=link,
                        image_url='',
                        summary=title[:200],
                        published_date=timezone.now() - timedelta(hours=added),
                        category=self.categorize(title),
                        is_active=True,
                        is_featured=False
                    )
                    added += 1
                    
                except Exception:
                    pass
        
        except Exception as e:
            raise Exception(f'Erro no scraping Folha: {str(e)}')
        
        return added

    def scrape_estadao_transito(self):
        """Scraping do Estadão - mobilidade"""
        added = 0
        
        try:
            url = 'https://www.estadao.com.br/mobilidade/'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('h3')[:10]
            
            for article in articles:
                try:
                    link_tag = article.find('a')
                    if not link_tag:
                        continue
                    
                    title = link_tag.get_text(strip=True)
                    link = link_tag.get('href', '')
                    
                    if not link.startswith('http'):
                        link = 'https://www.estadao.com.br' + link
                    
                    if NewsArticle.objects.filter(source_url=link).exists():
                        continue
                    
                    slug = slugify(title)[:250]
                    
                    NewsArticle.objects.create(
                        title=title,
                        slug=slug,
                        source='Estadão',
                        source_url=link,
                        image_url='',
                        summary=title[:200],
                        published_date=timezone.now() - timedelta(hours=added),
                        category=self.categorize(title),
                        is_active=True,
                        is_featured=False
                    )
                    added += 1
                    
                except Exception:
                    pass
        
        except Exception as e:
            raise Exception(f'Erro no scraping Estadão: {str(e)}')
        
        return added

    def fetch_article_details(self, url):
        """Busca detalhes adicionais de um artigo"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tenta pegar imagem Open Graph
            og_image = soup.find('meta', property='og:image')
            image = og_image.get('content', '') if og_image else ''
            
            # Tenta pegar descrição
            og_desc = soup.find('meta', property='og:description')
            summary = og_desc.get('content', '') if og_desc else ''
            
            return {'image': image, 'summary': summary}
        except Exception:
            return {'image': '', 'summary': ''}

    def categorize(self, text):
        """Categoriza notícia por palavras-chave"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['lei', 'legislação', 'norma']):
            return 'legislacao'
        elif any(word in text_lower for word in ['habilitação', 'cnh', 'carteira']):
            return 'habilitacao'
        elif any(word in text_lower for word in ['multa', 'infração', 'ponto']):
            return 'multas'
        elif any(word in text_lower for word in ['tecnologia', 'app', 'digital']):
            return 'tecnologia'
        elif any(word in text_lower for word in ['acidente', 'segurança']):
            return 'seguranca'
        
        return 'outros'
