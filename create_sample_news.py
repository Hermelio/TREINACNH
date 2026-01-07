#!/usr/bin/env python
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import NewsArticle

# Gerar datas recentes
now = datetime.now()
news_data = [
    {
        'title': 'Novas Regras do DETRAN Entram em Vigor em 2026',
        'slug': 'novas-regras-detran-2026',
        'summary': 'O DETRAN anunciou mudanças importantes para o processo de habilitação.',
        'content': 'O DETRAN anunciou novas regras para a habilitação que começam a valer em janeiro de 2026. As mudanças incluem maior rigor nas provas práticas e teóricas.',
        'source': 'Portal DETRAN',
        'source_url': 'https://www.detran.gov.br/noticias',
        'image_url': 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=800&q=80',
        'published_date': now - timedelta(days=1),
        'category': 'legislacao',
        'is_featured': True,
        'is_active': True,
    },
    {
        'title': 'CNH Digital Agora Pode Ser Renovada Pelo App',
        'slug': 'cnh-digital-renovacao-app',
        'summary': 'Renovação facilitada através do aplicativo oficial.',
        'content': 'A renovação da CNH digital agora pode ser feita diretamente pelo aplicativo oficial do DETRAN, facilitando o processo para os motoristas.',
        'source': 'G1',
        'source_url': 'https://g1.globo.com/noticias',
        'image_url': 'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800&q=80',
        'published_date': now - timedelta(days=2),
        'category': 'tecnologia',
        'is_featured': True,
        'is_active': True,
    },
    {
        'title': 'Dicas Para Passar na Prova Prática de Direção',
        'slug': 'dicas-prova-pratica',
        'summary': 'Confira as melhores dicas de instrutores profissionais.',
        'content': 'Confira as melhores dicas de instrutores profissionais para ter sucesso na sua prova prática de direção.',
        'source': 'TreinaCNH',
        'source_url': 'https://treinacnh.com.br',
        'image_url': 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=800&q=80',
        'published_date': now - timedelta(days=3),
        'category': 'habilitacao',
        'is_featured': False,
        'is_active': True,
    },
    {
        'title': 'Simulado Online Grátis Para a Prova do DETRAN',
        'slug': 'simulado-online-gratis',
        'summary': 'Pratique com questões atualizadas.',
        'content': 'Pratique para sua prova teórica com nosso simulado gratuito com questões atualizadas do DETRAN.',
        'source': 'TreinaCNH',
        'source_url': 'https://treinacnh.com.br',
        'image_url': 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800&q=80',
        'published_date': now - timedelta(days=5),
        'category': 'habilitacao',
        'is_featured': False,
        'is_active': True,
    },
    {
        'title': 'Quanto Custa Tirar a Carteira de Motorista em 2025',
        'slug': 'quanto-custa-carteira-2025',
        'summary': 'Todos os custos envolvidos no processo de habilitação.',
        'content': 'Descubra todos os custos envolvidos no processo de obtenção da CNH, incluindo taxas, aulas e exames.',
        'source': 'Portal do Trânsito',
        'source_url': 'https://portaldotransito.com.br',
        'image_url': 'https://images.unsplash.com/photo-1554224311-beee460c201a?w=800&q=80',
        'published_date': now - timedelta(days=7),
        'category': 'habilitacao',
        'is_featured': False,
        'is_active': True,
    },
]

created = 0
updated = 0
for data in news_data:
    # Adicionar timezone
    if data['published_date'].tzinfo is None:
        from django.utils import timezone
        data['published_date'] = timezone.make_aware(data['published_date'])
    
    obj, is_created = NewsArticle.objects.update_or_create(
        slug=data['slug'],
        defaults=data
    )
    if is_created:
        created += 1
        print(f'✓ Criada: {data["title"]}')
    else:
        updated += 1
        print(f'↻ Atualizada: {data["title"]}')

print(f'\n✅ {created} notícias criadas, {updated} atualizadas!')
print(f'📊 Total no banco: {NewsArticle.objects.count()}')
