#!/bin/bash
# Script para atualizar sistema de pagamentos no servidor

echo "=== INSTALAÇÃO SISTEMA DE PAGAMENTOS MERCADO PAGO ==="
echo ""

# Ativar venv
source /var/www/TREINACNH/venv/bin/activate

# Instalar mercadopago SDK
echo "1. Instalando Mercado Pago SDK..."
pip install mercadopago==2.2.3

# Adicionar variáveis ao .env
echo ""
echo "2. Configurando variáveis de ambiente..."
cd /var/www/TREINACNH

# Verificar se já existe
if ! grep -q "MERCADOPAGO_PUBLIC_KEY" .env 2>/dev/null; then
    echo "MERCADOPAGO_PUBLIC_KEY=APP_USR-2c64879c-db66-4546-a8ba-f9daa7851269" >> .env
    echo "MERCADOPAGO_ACCESS_TOKEN=APP_USR-252257382533300-011222-d7003683caae3927fb199a49ab7fd0a4-3130461427" >> .env
    echo "✓ Credenciais adicionadas ao .env"
else
    echo "✓ Credenciais já existem no .env"
fi

# Fazer migrations
echo ""
echo "3. Criando migrations do modelo Payment..."
python manage.py makemigrations billing

echo ""
echo "4. Aplicando migrations..."
python manage.py migrate

# Coletar arquivos estáticos
echo ""
echo "5. Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Reiniciar Gunicorn
echo ""
echo "6. Reiniciando Gunicorn..."
sudo pkill -HUP gunicorn

echo ""
echo "=== INSTALAÇÃO COMPLETA ==="
echo ""
echo "✓ SDK instalado"
echo "✓ Modelo Payment criado"
echo "✓ Migrations aplicadas"
echo "✓ Servidor reiniciado"
echo ""
echo "PRÓXIMOS PASSOS:"
echo "1. Testar checkout: http://72.61.36.89:8080/planos/minha-assinatura/"
echo "2. Configurar webhook no Mercado Pago:"
echo "   URL: http://72.61.36.89:8080/webhook/mercadopago/"
echo "   Eventos: payment.created, payment.updated"
echo ""
