# Automação de Scraping de Notícias

## 📅 Cron Jobs Configurados

O servidor possui automação configurada para buscar notícias automaticamente.

### Horários de Execução

```bash
# Scraping de notícias: 2x por dia (6h e 18h)
0 6,18 * * * /var/www/TREINACNH/scripts/scrape_news_daily.sh
```

### Script de Scraping

**Localização:** `/var/www/TREINACNH/scripts/scrape_news_daily.sh`

```bash
#!/bin/bash
# Script para scraping diário de notícias

cd /var/www/TREINACNH
source venv/bin/activate

# Log com timestamp
echo "=== Scraping iniciado em $(date) ===" >> logs/scrape_news.log
python manage.py scrape_news >> logs/scrape_news.log 2>&1
echo "=== Scraping finalizado em $(date) ===" >> logs/scrape_news.log
echo "" >> logs/scrape_news.log
```

## 🔧 Gerenciar Cron Jobs

### Ver cron jobs ativos

```bash
ssh root@72.61.36.89 'crontab -l'
```

### Editar cron jobs

```bash
ssh root@72.61.36.89 'crontab -e'
```

### Adicionar novo horário

Para adicionar mais horários de scraping, edite o crontab:

```bash
# Formato: minuto hora dia mês dia_da_semana comando
# Exemplos:
0 6,12,18 * * * /var/www/TREINACNH/scripts/scrape_news_daily.sh  # 3x por dia (6h, 12h, 18h)
0 */6 * * * /var/www/TREINACNH/scripts/scrape_news_daily.sh      # A cada 6 horas
0 6 * * * /var/www/TREINACNH/scripts/scrape_news_daily.sh        # 1x por dia (6h)
```

### Remover cron job

```bash
ssh root@72.61.36.89 'crontab -r'  # Remove TODOS os cron jobs
```

## 📊 Monitorar Execução

### Ver log de scraping

```bash
ssh root@72.61.36.89 'cat /var/www/TREINACNH/logs/scrape_news.log'
```

### Ver últimas 50 linhas do log

```bash
ssh root@72.61.36.89 'tail -50 /var/www/TREINACNH/logs/scrape_news.log'
```

### Ver log em tempo real

```bash
ssh root@72.61.36.89 'tail -f /var/www/TREINACNH/logs/scrape_news.log'
```

### Limpar log antigo

```bash
ssh root@72.61.36.89 'echo "" > /var/www/TREINACNH/logs/scrape_news.log'
```

## ▶️ Executar Manualmente

### Executar script diretamente

```bash
ssh root@72.61.36.89 '/var/www/TREINACNH/scripts/scrape_news_daily.sh'
```

### Executar comando Django

```bash
ssh root@72.61.36.89 'cd /var/www/TREINACNH && source venv/bin/activate && python manage.py scrape_news'
```

## 🐛 Troubleshooting

### Cron não está executando?

1. Verifique se o cron service está rodando:
   ```bash
   ssh root@72.61.36.89 'systemctl status cron'
   ```

2. Verifique se o script tem permissão de execução:
   ```bash
   ssh root@72.61.36.89 'ls -la /var/www/TREINACNH/scripts/scrape_news_daily.sh'
   ```

3. Teste o script manualmente:
   ```bash
   ssh root@72.61.36.89 '/var/www/TREINACNH/scripts/scrape_news_daily.sh'
   ```

### Script retorna 0 notícias?

Isso pode acontecer se:
- Os sites mudaram a estrutura HTML
- Há bloqueio por User-Agent
- Problemas de conectividade
- Sites com proteção anti-bot

**Solução temporária:** Use o script `create_sample_news.py` para adicionar notícias manualmente.

## 📧 Notificações (Opcional)

Para receber emails quando o cron executar, configure o email no crontab:

```bash
MAILTO="seu@email.com"
0 6,18 * * * /var/www/TREINACNH/scripts/scrape_news_daily.sh
```

## 🔄 Atualizar Script

1. Edite localmente: `scripts/scrape_news_daily.sh`
2. Envie para o servidor:
   ```bash
   scp scripts/scrape_news_daily.sh root@72.61.36.89:/var/www/TREINACNH/scripts/
   ```
3. Dê permissão de execução:
   ```bash
   ssh root@72.61.36.89 'chmod +x /var/www/TREINACNH/scripts/scrape_news_daily.sh'
   ```

## ⏰ Horários Recomendados

- **6h da manhã:** Captura notícias da madrugada/início do dia
- **18h da tarde:** Captura notícias do dia
- **12h meio-dia:** (Opcional) Captura notícias da manhã

## 📋 Outros Cron Jobs Configurados

```bash
# Renovação automática de certificados SSL (meio-dia)
0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔍 Verificar Status

### Última execução do cron

```bash
ssh root@72.61.36.89 'grep scrape_news /var/log/syslog | tail -5'
```

### Logs do sistema

```bash
ssh root@72.61.36.89 'journalctl -u cron | tail -20'
```
