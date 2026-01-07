# Instalação do Tesseract OCR

## Windows

### Passo 1: Baixar o Instalador

1. Acesse: https://github.com/UB-Mannheim/tesseract/wiki
2. Baixe a versão mais recente (ex: `tesseract-ocr-w64-setup-5.3.3.exe`)

### Passo 2: Instalar

1. Execute o instalador
2. **IMPORTANTE**: Durante a instalação, marque:
   - ✅ Tesseract
   - ✅ Additional language data (download)
   - ✅ Portuguese (por) language pack
3. Caminho de instalação padrão: `C:\Program Files\Tesseract-OCR`
4. Clique em "Install"

### Passo 3: Verificar Instalação

Abra o PowerShell e execute:

```powershell
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
```

Você deve ver algo como:
```
tesseract 5.3.3
 leptonica-1.83.1
  libgif 5.2.1 : libjpeg 8d (libjpeg-turbo 2.1.5.1) : libpng 1.6.40 : libtiff 4.5.1 : zlib 1.2.13 : libwebp 1.3.2 : libopenjp2 2.5.0
```

### Passo 4: Testar OCR

Baixe uma imagem de teste e execute:

```powershell
& "C:\Program Files\Tesseract-OCR\tesseract.exe" teste.jpg saida -l por
Get-Content saida.txt
```

---

## Linux (Ubuntu/Debian)

### Instalar Tesseract + Português

```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-por
```

### Verificar

```bash
tesseract --version
tesseract --list-langs
```

---

## macOS

### Instalar com Homebrew

```bash
brew install tesseract tesseract-lang
```

### Verificar

```bash
tesseract --version
tesseract --list-langs | grep por
```

---

## Configuração no Django

O código já está configurado para encontrar automaticamente o Tesseract no Windows.

Veja em `verification/services.py`:

```python
import pytesseract
import os

if os.name == 'nt':  # Windows
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break
```

Se instalou em um caminho diferente, edite manualmente:

```python
pytesseract.pytesseract.tesseract_cmd = r'C:\SEU\CAMINHO\tesseract.exe'
```

---

## Teste Rápido no Django

Acesse o shell do Django:

```bash
python manage.py shell
```

Execute:

```python
from verification.services import DocumentVerificationService
import os

# Teste se Tesseract está acessível
import pytesseract
print(pytesseract.get_tesseract_version())

# Teste OCR em uma imagem (coloque uma imagem de teste em media/)
service = DocumentVerificationService()
result = service.extract_cnh_data('media/test_cnh.jpg')
print(result)
```

---

## Solução de Problemas

### Erro: "tesseract is not installed or it's not in your PATH"

**Windows:**
```python
# Adicione manualmente em services.py:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Linux/Mac:**
```bash
# Verifique se está instalado:
which tesseract

# Se não estiver no PATH, instale novamente
```

### Erro: "Failed loading language 'por'"

**Solução:** Reinstale com o pacote de idioma português:

**Windows:** Execute o instalador novamente e marque "Portuguese"

**Linux:**
```bash
sudo apt install tesseract-ocr-por
```

**Mac:**
```bash
brew reinstall tesseract tesseract-lang
```

### OCR não está extraindo dados corretamente

1. **Melhore a qualidade da imagem:**
   - Use fotos nítidas e bem iluminadas
   - Evite sombras e reflexos
   - Resolução mínima: 300 DPI

2. **Pré-processamento está ativado:**
   O código já aplica:
   - Conversão para escala de cinza
   - Redução de ruído
   - Binarização (threshold)

3. **Teste com diferentes imagens:**
   - CNH nova (padrão atual)
   - CNH digitalizada
   - Foto tirada com celular

---

## Verificação Final

Se tudo estiver correto:

1. ✅ Tesseract instalado
2. ✅ Pacote de idioma português instalado
3. ✅ Caminho configurado no código
4. ✅ Bibliotecas Python instaladas (pytesseract, opencv-python, Pillow)
5. ✅ Teste manual funcionando

**Pronto!** O sistema de verificação de documentos está completo e funcional.

---

## Referências

- Tesseract GitHub: https://github.com/tesseract-ocr/tesseract
- Windows Builds: https://github.com/UB-Mannheim/tesseract/wiki
- pytesseract Documentation: https://pypi.org/project/pytesseract/
- OpenCV Python: https://pypi.org/project/opencv-python/
