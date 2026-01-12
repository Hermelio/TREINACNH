# Imagens Necessárias - TreinaCNH

## Para a Home Page (Hero Section)

### 1. logohome.png
**Descrição:** Imagem principal do hero section da home page  
**Uso:** Background da seção hero no estilo Uber  
**Dimensões recomendadas:** 1920x1080px ou superior  
**Formato:** PNG ou JPG de alta qualidade  
**Localização:** `static/images/logohome.png`

**Características da imagem ideal:**
- Mostra um instrutor de direção em ação
- Ambiente profissional (carro, instrutor, contexto de aula)
- Boa iluminação
- Resolução alta para suportar telas grandes
- A imagem terá um overlay escuro (60-75%) sobre ela para garantir legibilidade do texto

### 2. logo-treinacnh.png
**Descrição:** Logo oficial do projeto TreinaCNH  
**Uso:** Logo principal do site (navbar, footer, etc)  
**Formato:** PNG com transparência  
**Dimensões:** 200x60px aproximadamente  
**Localização:** `static/images/logo-treinacnh.png`

## Como Adicionar as Imagens

1. Salve as imagens com os nomes exatos especificados acima
2. Coloque os arquivos na pasta `static/images/`
3. Execute no servidor:
   ```bash
   python manage.py collectstatic --noinput
   ```
4. Reinicie o Gunicorn:
   ```bash
   kill -HUP $(cat /var/run/gunicorn.pid)
   ```

## Status Atual

- ❌ `logohome.png` - **PENDENTE** (hero section está usando fallback gradient)
- ✅ `logo.png` - Existe (pode ser usado ou substituído pelo logo-treinacnh.png)

## Depois de Adicionar as Imagens no Servidor

```bash
# No servidor
cd /var/www/TREINACNH
# Fazer upload das imagens para static/images/
python manage.py collectstatic --noinput
kill -HUP 1132837
```
