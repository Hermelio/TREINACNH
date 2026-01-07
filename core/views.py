"""
Views for core app - Public pages.
"""
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, OuterRef, Subquery
from marketplace.models import State, City, InstructorProfile
from .models import StaticPage, FAQEntry, HomeBanner, NewsArticle


def home_view(request):
    """Homepage with search, featured instructors and interactive map"""
    import json
    
    # Get instructor count per state
    instructor_counts = InstructorProfile.objects.filter(
        is_visible=True,
        city__state=OuterRef('pk')
    ).values('city__state').annotate(
        total=Count('id')
    ).values('total')
    
    # Get states for search dropdown with instructor counts
    states = State.objects.annotate(
        instructor_count=Subquery(instructor_counts)
    ).order_by('code')
    
    # Featured/new instructors
    from django.utils import timezone
    from datetime import timedelta
    featured_instructors = InstructorProfile.objects.filter(
        is_visible=True,
        is_verified=True
    ).select_related('user', 'user__profile', 'city', 'city__state').order_by('-created_at')[:6]
    
    # Stats
    total_instructors = InstructorProfile.objects.filter(is_visible=True, is_verified=True).count()
    total_cities = City.objects.filter(is_active=True).annotate(
        instructor_count=Count('instructors', filter=Q(instructors__is_visible=True))
    ).filter(instructor_count__gt=0).count()
    
    # Banners
    banners = HomeBanner.objects.filter(is_active=True).order_by('order')[:3]
    
    # Get all instructors with coordinates for map markers
    instructors_with_location = InstructorProfile.objects.filter(
        is_visible=True,
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related('user', 'city', 'city__state')
    
    # Convert to list with float coordinates
    instructors_data = []
    for inst in instructors_with_location:
        instructors_data.append({
            'id': inst.id,
            'user__first_name': inst.user.first_name,
            'user__last_name': inst.user.last_name,
            'latitude': float(inst.latitude),
            'longitude': float(inst.longitude),
            'city__name': inst.city.name,
            'city__state__code': inst.city.state.code,
            'city__state__name': inst.city.state.name
        })
    
    # Prepare data for map
    states_data = []
    for state in states:
        coords = None
        if state.latitude and state.longitude:
            coords = [float(state.latitude), float(state.longitude)]
        
        states_data.append({
            'code': state.code,
            'name': state.name,
            'instructors': state.instructor_count or 0,
            'coordinates': coords
        })
    
    context = {
        'states': states,
        'states_json': json.dumps(states_data),
        'instructors_json': json.dumps(instructors_data),
        'featured_instructors': featured_instructors,
        'total_instructors': total_instructors,
        'total_cities': total_cities,
        'banners': banners,
        'page_title': 'Encontre seu Instrutor de Direção',
    }
    return render(request, 'core/home.html', context)


def about_view(request):
    """About us page"""
    context = {'page_title': 'Sobre Nós'}
    return render(request, 'core/about.html', context)


def contact_view(request):
    """Contact page"""
    if request.method == 'POST':
        from django.contrib import messages
        messages.success(request, 'Mensagem enviada com sucesso! Responderemos em breve.')
    
    context = {'page_title': 'Contato'}
    return render(request, 'core/contact.html', context)


def faq_view(request):
    """FAQ page"""
    faqs = FAQEntry.objects.filter(is_active=True).order_by('category', 'order')
    
    # Group by category
    from itertools import groupby
    grouped_faqs = {}
    for category, items in groupby(faqs, key=lambda x: x.category):
        grouped_faqs[category] = list(items)
    
    context = {
        'grouped_faqs': grouped_faqs,
        'page_title': 'Perguntas Frequentes',
    }
    return render(request, 'core/faq.html', context)


def static_page_view(request, slug):
    """Generic static page view"""
    page = get_object_or_404(StaticPage, slug=slug, is_active=True)
    context = {
        'page': page,
        'page_title': page.title,
    }
    return render(request, 'core/static_page.html', context)


def healthcheck_view(request):
    """Simple healthcheck endpoint for monitoring"""
    from django.http import JsonResponse
    from django.db import connection
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return JsonResponse({
        'status': 'ok' if db_status == 'ok' else 'error',
        'database': db_status,
    })


# Import models for home_view
from django.db import models


def news_list_view(request):
    """Lista de notícias sobre DETRAN e trânsito"""
    category = request.GET.get('category', '')
    
    news_queryset = NewsArticle.objects.filter(is_active=True)
    
    if category:
        news_queryset = news_queryset.filter(category=category)
    
    # Notícias em destaque
    featured_news = news_queryset.filter(is_featured=True)[:3]
    
    # Converter para lista de IDs antes do exclude (fix MySQL LIMIT in subquery)
    featured_ids = list(featured_news.values_list('id', flat=True))
    
    # Todas as notícias exceto as em destaque
    all_news = news_queryset.exclude(id__in=featured_ids)
    
    # Categorias para filtro
    categories = NewsArticle.CATEGORY_CHOICES
    
    context = {
        'featured_news': featured_news,
        'all_news': all_news,
        'categories': categories,
        'selected_category': category,
    }
    
    return render(request, 'core/news_list.html', context)


def news_detail_view(request, slug):
    """Detalhes de uma notícia"""
    news = get_object_or_404(NewsArticle, slug=slug, is_active=True)
    
    # Notícias relacionadas (mesma categoria)
    related_news = NewsArticle.objects.filter(
        category=news.category,
        is_active=True
    ).exclude(id=news.id)[:4]
    
    context = {
        'news': news,
        'related_news': related_news,
    }
    
    return render(request, 'core/news_detail.html', context)
