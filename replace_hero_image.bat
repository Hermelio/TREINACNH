@echo off
echo ======================================================================
echo SUBSTITUICAO DA IMAGEM HERO - SEM LOGOS DE TERCEIROS
echo ======================================================================
echo.

REM Verificar se a imagem existe
if not exist "hero-instructor-clean.jpg" (
    echo ❌ ERRO: Imagem 'hero-instructor-clean.jpg' nao encontrada!
    echo.
    echo Por favor:
    echo 1. Clique com botao direito na imagem anexada
    echo 2. Salve como 'hero-instructor-clean.jpg' neste diretorio
    echo 3. Execute este script novamente
    echo.
    pause
    exit /b 1
)

echo ✅ Imagem encontrada!
echo.
echo Enviando para o servidor...
scp hero-instructor-clean.jpg root@72.61.36.89:/var/www/TREINACNH/

echo.
echo Enviando script de processamento...
scp process_hero_image.py root@72.61.36.89:/var/www/TREINACNH/

echo.
echo Instalando dependencias no servidor...
ssh root@72.61.36.89 "cd /var/www/TREINACNH && venv/bin/pip install Pillow pillow-avif-plugin"

echo.
echo Processando imagens no servidor...
ssh root@72.61.36.89 "cd /var/www/TREINACNH && venv/bin/python process_hero_image.py"

echo.
echo ======================================================================
echo ✅ IMAGENS SUBSTITUIDAS COM SUCESSO!
echo ======================================================================
echo.
echo A pagina inicial agora usa a nova imagem sem logos de terceiros.
echo.
pause
