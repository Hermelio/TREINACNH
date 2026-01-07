"""
Models for core app - Static pages, FAQ, banners.
"""
from django.db import models


class StaticPage(models.Model):
    """Static content pages (Terms, Privacy, About, etc.)"""
    title = models.CharField('Título', max_length=200)
    slug = models.SlugField('Slug', unique=True)
    content = models.TextField('Conteúdo', help_text='Suporta HTML')
    is_active = models.BooleanField('Ativo', default=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Página Estática'
        verbose_name_plural = 'Páginas Estáticas'
        ordering = ['title']
    
    def __str__(self):
        return self.title


class FAQEntry(models.Model):
    """FAQ entries"""
    question = models.CharField('Pergunta', max_length=300)
    answer = models.TextField('Resposta')
    category = models.CharField(
        'Categoria',
        max_length=50,
        choices=[
            ('STUDENT', 'Para Alunos'),
            ('INSTRUCTOR', 'Para Instrutores'),
            ('GENERAL', 'Geral'),
        ],
        default='GENERAL'
    )
    order = models.PositiveIntegerField('Ordem', default=0)
    is_active = models.BooleanField('Ativo', default=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQ'
        ordering = ['category', 'order', 'question']
    
    def __str__(self):
        return self.question


class HomeBanner(models.Model):
    """Homepage banners/highlights"""
    title = models.CharField('Título', max_length=200)
    subtitle = models.CharField('Subtítulo', max_length=300, blank=True)
    image = models.ImageField('Imagem', upload_to='banners/', blank=True, null=True)
    link_url = models.URLField('Link', blank=True)
    link_text = models.CharField('Texto do Link', max_length=100, blank=True)
    
    order = models.PositiveIntegerField('Ordem', default=0)
    is_active = models.BooleanField('Ativo', default=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Banner da Home'
        verbose_name_plural = 'Banners da Home'
        ordering = ['order']
    
    def __str__(self):
        return self.title


class NewsArticle(models.Model):
    """Notícias sobre DETRAN e trânsito"""
    title = models.CharField('Título', max_length=300)
    slug = models.SlugField('Slug', unique=True, max_length=300)
    source = models.CharField('Fonte', max_length=200, help_text='Ex: G1, UOL, Folha')
    source_url = models.URLField('URL da Fonte')
    image_url = models.URLField('URL da Imagem', blank=True, null=True)
    summary = models.TextField('Resumo', help_text='Breve descrição da notícia')
    content = models.TextField('Conteúdo', blank=True, help_text='Conteúdo completo (opcional)')
    published_date = models.DateTimeField('Data de Publicação')
    
    # Categorias
    CATEGORY_CHOICES = [
        ('legislacao', 'Legislação'),
        ('habilitacao', 'Habilitação'),
        ('multas', 'Multas e Infrações'),
        ('tecnologia', 'Tecnologia'),
        ('seguranca', 'Segurança no Trânsito'),
        ('outros', 'Outros'),
    ]
    category = models.CharField('Categoria', max_length=20, choices=CATEGORY_CHOICES, default='outros')
    
    is_featured = models.BooleanField('Destaque', default=False)
    is_active = models.BooleanField('Ativo', default=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Notícia'
        verbose_name_plural = 'Notícias'
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['-published_date']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.title
