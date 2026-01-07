# Gerenciamento de Notícias

## 📰 Sistema de Notícias

O sistema de notícias do TreinaCNH exibe notícias sobre DETRAN, habilitação e trânsito.

### Estrutura do Modelo NewsArticle

```python
- title: Título da notícia (max 300 caracteres)
- slug: Identificador único para URL
- source: Fonte da notícia (ex: G1, UOL, DETRAN)
- source_url: URL da notícia original
- image_url: URL da imagem da notícia (opcional)
- summary: Resumo breve da notícia
- content: Conteúdo completo (opcional)
- published_date: Data de publicação
- category: Categoria (legislacao, habilitacao, multas, tecnologia, seguranca, outros)
- is_featured: Destaque na página inicial
- is_active: Ativo/Inativo
```

## 🔧 Criar Notícias Manualmente

### Método 1: Via Script Python

Use o script `create_sample_news.py`:

```bash
# No servidor
cd /var/www/TREINACNH
source venv/bin/activate
python create_sample_news.py
```

### Método 2: Via Django Admin

1. Acesse: http://72.61.36.89:8080/admin/
2. Faça login com superusuário
3. Vá em Core → Notícias
4. Clique em "Adicionar Notícia"
5. Preencha os campos e salve

### Método 3: Via Shell Django

```bash
cd /var/www/TREINACNH
source venv/bin/activate
python manage.py shell

# No shell:
from core.models import NewsArticle
from django.utils import timezone
from datetime import datetime

NewsArticle.objects.create(
    title='Título da Notícia',
    slug='titulo-da-noticia',
    source='Fonte',
    source_url='https://fonte.com.br',
    summary='Resumo da notícia',
    content='Conteúdo completo...',
    published_date=timezone.now(),
    category='legislacao',
    is_featured=True,
    is_active=True
)
```

## 🕷️ Web Scraping de Notícias

### Comando de Scraping

```bash
cd /var/www/TREINACNH
source venv/bin/activate
python manage.py scrape_news
```

### Fontes Configuradas

- G1
- UOL
- Folha de S.Paulo
- Estadão

### Nota Sobre Scraping

⚠️ **O scraping pode falhar se:**
- Os sites mudarem a estrutura HTML
- Houver bloqueio por User-Agent
- Problemas de conectividade
- Sites com proteção anti-bot

**Solução:** Use criação manual ou via API se disponível.

## 📊 Consultar Notícias

### Contar notícias no banco:

```bash
ssh root@72.61.36.89 "echo 'SELECT COUNT(*) FROM core_newsarticle;' | sudo mysql treinacnh"
```

### Listar últimas notícias:

```bash
ssh root@72.61.36.89 "echo 'SELECT title, published_date FROM core_newsarticle ORDER BY published_date DESC LIMIT 5;' | sudo mysql treinacnh"
```

### Via Django Shell:

```python
from core.models import NewsArticle

# Total
print(NewsArticle.objects.count())

# Últimas 5
for news in NewsArticle.objects.all()[:5]:
    print(f"- {news.title}")

# Notícias em destaque
for news in NewsArticle.objects.filter(is_featured=True):
    print(f"⭐ {news.title}")
```

## 🔄 Atualizar Notícias Existentes

```python
# Via shell
from core.models import NewsArticle

news = NewsArticle.objects.get(slug='slug-da-noticia')
news.title = 'Novo Título'
news.is_featured = True
news.save()
```

## 🗑️ Deletar Notícias

```python
# Deletar por slug
NewsArticle.objects.filter(slug='noticia-antiga').delete()

# Deletar todas (CUIDADO!)
# NewsArticle.objects.all().delete()
```

## 📄 Páginas de Notícias

- **Lista de notícias:** http://72.61.36.89:8080/noticias/
- **Detalhes:** http://72.61.36.89:8080/noticias/[slug]/

## 🎨 Categorias Disponíveis

- `legislacao` - Legislação
- `habilitacao` - Habilitação
- `multas` - Multas e Infrações
- `tecnologia` - Tecnologia
- `seguranca` - Segurança no Trânsito
- `outros` - Outros

## ⚙️ Configurações

As notícias são exibidas:
- Na página `/noticias/` (todas as notícias)
- Na home page (notícias em destaque com `is_featured=True`)
- Ordenadas por data de publicação (mais recentes primeiro)

## 🐛 Troubleshooting

### Notícias não aparecem?

1. Verifique se existem notícias no banco:
   ```bash
   ssh root@72.61.36.89 "echo 'SELECT COUNT(*) FROM core_newsarticle WHERE is_active=1;' | sudo mysql treinacnh"
   ```

2. Verifique logs:
   ```bash
   ssh root@72.61.36.89 'tail -50 /var/www/TREINACNH/logs/gunicorn-error.log'
   ```

3. Teste a view:
   ```bash
   ssh root@72.61.36.89 'curl -I http://127.0.0.1:8001/noticias/'
   ```

### Erro 500 na página de notícias?

Verifique compatibilidade MySQL no `core/views.py`:
- Não use LIMIT em subqueries com IN
- Converta querysets para listas antes de exclude

### Scraping retorna 0 notícias?

- Sites podem ter mudado HTML
- Use criação manual como alternativa
- Verifique conectividade do servidor
