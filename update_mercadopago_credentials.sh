#!/bin/bash
# Script para atualizar credenciais do Mercado Pago no servidor
# Execute este script no servidor: bash update_mercadopago_credentials.sh

echo "=========================================="
echo "ATUALIZAÇÃO DE CREDENCIAIS MERCADO PAGO"
echo "=========================================="
echo ""

# Caminho do arquivo .env
ENV_FILE="/var/www/TREINACNH/.env"

echo "Você tem as novas credenciais do Mercado Pago?"
echo ""
echo "Para obter suas credenciais:"
echo "1. Acesse: https://www.mercadopago.com.br/developers/panel"
echo "2. Vá em 'Suas integrações' > Escolha sua aplicação"
echo "3. Vá em 'Credenciais de produção' ou 'Credenciais de teste'"
echo "4. Copie o ACCESS TOKEN e PUBLIC KEY"
echo ""

read -p "Digite o MERCADOPAGO_PUBLIC_KEY (APP_USR-...): " PUBLIC_KEY
echo ""
read -p "Digite o MERCADOPAGO_ACCESS_TOKEN (APP_USR-...): " ACCESS_TOKEN
echo ""

if [ -z "$PUBLIC_KEY" ] || [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Erro: Credenciais não podem estar vazias!"
    exit 1
fi

# Fazer backup do .env atual
echo "Fazendo backup do arquivo .env atual..."
cp $ENV_FILE ${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)

# Atualizar ou adicionar as credenciais
echo "Atualizando credenciais no arquivo .env..."

# Remover linhas antigas se existirem
sed -i '/^MERCADOPAGO_PUBLIC_KEY=/d' $ENV_FILE
sed -i '/^MERCADOPAGO_ACCESS_TOKEN=/d' $ENV_FILE

# Adicionar novas credenciais
echo "MERCADOPAGO_PUBLIC_KEY=$PUBLIC_KEY" >> $ENV_FILE
echo "MERCADOPAGO_ACCESS_TOKEN=$ACCESS_TOKEN" >> $ENV_FILE

echo ""
echo "✅ Credenciais atualizadas com sucesso!"
echo ""
echo "Reiniciando serviço Django..."
sudo systemctl restart treinacnh.service

sleep 2

echo ""
echo "Testando conexão com Mercado Pago..."
cd /var/www/TREINACNH
source venv/bin/activate
python test_mercadopago.py

echo ""
echo "=========================================="
echo "Atualização concluída!"
echo "=========================================="
echo ""
echo "📝 Notas importantes:"
echo "  - Backup salvo em: ${ENV_FILE}.backup.*"
echo "  - Webhook URL: http://72.61.36.89:8080/webhook/mercadopago/"
echo "  - Configure o webhook no painel do Mercado Pago"
echo ""
