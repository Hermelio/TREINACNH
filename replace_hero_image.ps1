# Script para substituir imagem hero no servidor
Write-Host "======================================================================"
Write-Host "SUBSTITUICAO DA IMAGEM HERO - SEM LOGOS DE TERCEIROS"
Write-Host "======================================================================"
Write-Host ""

# Verificar se a imagem existe
if (-not (Test-Path "hero-instructor-clean.jpg")) {
    Write-Host "❌ ERRO: Imagem 'hero-instructor-clean.jpg' nao encontrada!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor:"
    Write-Host "1. Clique com botao direito na imagem anexada no chat"
    Write-Host "2. Salve como 'hero-instructor-clean.jpg' neste diretorio"
    Write-Host "3. Execute este script novamente"
    Write-Host ""
    pause
    exit 1
}

Write-Host "✅ Imagem encontrada!" -ForegroundColor Green
Write-Host ""

Write-Host "📤 Enviando imagem para servidor..."
scp hero-instructor-clean.jpg root@72.61.36.89:/var/www/TREINACNH/

Write-Host ""
Write-Host "📤 Enviando script de processamento..."
scp process_hero_simple.py root@72.61.36.89:/var/www/TREINACNH/

Write-Host ""
Write-Host "📦 Instalando dependencias no servidor..."
ssh root@72.61.36.89 "cd /var/www/TREINACNH && venv/bin/pip install Pillow pillow-avif-plugin -q"

Write-Host ""
Write-Host "🖼️  Processando imagens no servidor..."
ssh root@72.61.36.89 cd /var/www/TREINACNH && venv/bin/python process_hero_simple.py"

Write-Host ""
Write-Host "======================================================================"
Write-Host "✅ IMAGENS SUBSTITUIDAS COM SUCESSO!" -ForegroundColor Green
Write-Host "======================================================================"
Write-Host ""
Write-Host "A pagina inicial agora usa a nova imagem sem logos de terceiros."
Write-Host "As imagens foram geradas em todos os formatos (AVIF, WebP, PNG)"
Write-Host ""
pause
