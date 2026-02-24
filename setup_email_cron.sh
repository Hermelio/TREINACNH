#!/bin/bash
# Configura o cron para enviar emails em blocos de 40 a cada 2 horas
CRON_LINE="0 */2 * * * cd /var/www/TREINACNH && source venv/bin/activate && python -u batch_send_emails.py >> /var/log/treinacnh_batch_email.log 2>&1"
# Adiciona apenas se ainda nao existir
( crontab -l 2>/dev/null | grep -v batch_send_emails; echo "$CRON_LINE" ) | crontab -
echo "Cron configurado:"
crontab -l | grep batch_send
