# Configuração da Logo - TREINACNH

## ✅ Implementação Concluída

A logo TreinaCNH.com.br/logo.png foi configurada como padrão em todo o projeto!

### 🎯 O que foi implementado:

1. **Estrutura de Diretórios**
   - Criada pasta `static/images/` para armazenar imagens
   - Preparada para receber a logo

2. **Configuração Django (settings.py)**
   - Adicionadas variáveis globais:
     - `SITE_NAME = 'TREINACNH'`
     - `SITE_LOGO = 'images/logo.png'`
     - `SITE_URL` (configurável via .env)

3. **Context Processor**
   - Criado `core/context_processors.py`
   - Disponibiliza em TODOS os templates:
     - `{{ site_name }}` - Nome do site
     - `{{ site_logo }}` - Caminho da logo
     - `{{ site_url }}` - URL do site

4. **Templates Atualizados**
   - ✅ Navbar: Logo com fallback automático para ícone
   - ✅ Footer: Logo exibida ao lado do nome
   - ✅ Sistema inteligente: Se a imagem não carregar, mostra o ícone

### 📥 Como adicionar a logo:

#### Opção 1: Download Manual
```bash
# 1. Acesse: https://TreinaCNH.com.br/logo.png
# 2. Salve o arquivo em:
static/images/logo.png
```

#### Opção 2: PowerShell (Recomendado)
```powershell
# Execute no terminal do VS Code:
Invoke-WebRequest -Uri "https://TreinaCNH.com.br/logo.png" -OutFile "static/images/logo.png"
```

#### Opção 3: Python
```python
import requests

url = "https://TreinaCNH.com.br/logo.png"
response = requests.get(url)

if response.status_code == 200:
    with open("static/images/logo.png", "wb") as f:
        f.write(response.content)
    print("✅ Logo baixada com sucesso!")
```

### 🔧 Personalização

#### Mudar a logo:
1. Substitua o arquivo `static/images/logo.png`
2. Ou edite `settings.py`:
```python
SITE_LOGO = 'images/sua-nova-logo.png'
```

#### Ajustar tamanho da logo:
Edite `templates/base.html`:
```css
/* Navbar */
.navbar-uber .navbar-brand img.site-logo {
    height: 40px;  /* ← Ajuste aqui */
}

/* Footer */
style="height: 30px;"  /* ← Ajuste aqui */
```

### 🎨 Uso da Logo em Outros Templates

A logo está disponível automaticamente em TODOS os templates:

```django
{% load static %}

<!-- Logo com fallback -->
{% if site_logo %}
    <img src="{% static site_logo %}" alt="{{ site_name }}">
{% endif %}

<!-- Nome do site -->
<h1>{{ site_name }}</h1>

<!-- URL do site -->
<a href="{{ site_url }}">Visite nosso site</a>
```

### 📋 Checklist Pós-Instalação

- [ ] Baixar logo de TreinaCNH.com.br/logo.png
- [ ] Salvar em `static/images/logo.png`
- [ ] Executar `python manage.py collectstatic` (produção)
- [ ] Verificar navbar e footer no navegador
- [ ] Ajustar tamanho se necessário

### 🚀 Próximos Passos Sugeridos

1. **Favicon**: Adicionar favicon do site
2. **Open Graph**: Configurar imagem para redes sociais
3. **Email Templates**: Usar logo nos emails do sistema
4. **PWA**: Adicionar ícones para Progressive Web App

### 📝 Arquivos Modificados

- ✅ `config/settings.py` - Configurações globais
- ✅ `core/context_processors.py` - Context processor (novo)
- ✅ `templates/base.html` - Navbar e footer atualizados
- ✅ `static/images/` - Estrutura criada
- ✅ `static/images/README.md` - Documentação da pasta

### 🆘 Troubleshooting

**Logo não aparece?**
1. Verifique se o arquivo existe em `static/images/logo.png`
2. Execute: `python manage.py collectstatic`
3. Limpe o cache do navegador (Ctrl+Shift+R)
4. Verifique o console do navegador (F12) para erros

**Ícone aparece em vez da logo?**
- Normal! É o fallback automático quando a logo não está disponível
- Basta adicionar a logo e recarregar a página

**Logo muito grande/pequena?**
- Ajuste `height` no CSS (navbar: 40px, footer: 30px)
- Mantenha `width: auto` para preservar proporção

---

**Status**: ✅ Pronto para uso
**Data**: 07/01/2026
**Versão**: 1.0
