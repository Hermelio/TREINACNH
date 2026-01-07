#!/bin/bash
# Script para scraping diário de notícias

cd /var/www/TREINACNH
source venv/bin/activate

# Log com timestamp
echo "=== Scraping iniciado em $(date) ===" >> logs/scrape_news.log
python manage.py scrape_news >> logs/scrape_news.log 2>&1
echo "=== Scraping finalizado em $(date) ===" >> logs/scrape_news.log
echo "" >> logs/scrape_news.log
