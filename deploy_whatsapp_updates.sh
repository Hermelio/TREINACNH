#!/bin/bash
# Script para fazer deploy das alterações do sistema de WhatsApp
# Execute no servidor como: bash deploy_whatsapp_updates.sh

echo "=== Iniciando deploy das alterações do sistema WhatsApp ==="

# Diretório do projeto
PROJECT_DIR="/home/treinacnh/treinacnh"
cd $PROJECT_DIR

echo "1. Fazendo backup dos arquivos atuais..."
cp marketplace/views.py marketplace/views.py.bak.$(date +%Y%m%d_%H%M%S)
cp templates/marketplace/my_leads.html templates/marketplace/my_leads.html.bak.$(date +%Y%m%d_%H%M%S)
cp templates/core/city_instructors.html templates/core/city_instructors.html.bak.$(date +%Y%m%d_%H%M%S)

echo "2. Atualizando arquivos do Git..."
git pull origin main

echo "3. Ativando ambiente virtual..."
source venv/bin/activate

echo "4. Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "5. Reiniciando serviços..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "6. Verificando status dos serviços..."
sudo systemctl status gunicorn --no-pager
sudo systemctl status nginx --no-pager

echo ""
echo "=== Deploy concluído! ==="
echo ""
echo "Alterações realizadas:"
echo "  ✓ Sistema de WhatsApp direto (já estava funcionando)"
echo "  ✓ Contador de visualizações de perfil (já existia)"
echo "  ✓ Painel do instrutor agora mostra APENAS alunos que clicaram no WhatsApp"
echo "  ✓ Dashboard com 3 cards: Perfil, Visualizações, Contatos WhatsApp"
echo "  ✓ Registro de cliques no WhatsApp em todas as páginas"
echo ""
echo "Teste no navegador:"
echo "  1. Acesse o perfil de um instrutor"
echo "  2. Clique no botão WhatsApp"
echo "  3. Faça login como instrutor e veja o painel de leads"
echo ""
