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
    from marketplace.models import StudentLead
    
    # Get instructor count per state
    instructor_counts = InstructorProfile.objects.filter(
        is_visible=True,
        city__state=OuterRef('pk')
    ).values('city__state').annotate(
        total=Count('id')
    ).values('total')
    
    # Get student lead count per state
    student_counts = StudentLead.objects.filter(
        state=OuterRef('pk')
    ).values('state').annotate(
        total=Count('id')
    ).values('total')
    
    # Get states for search dropdown with instructor and student counts
    states = State.objects.annotate(
        instructor_count=Subquery(instructor_counts),
        student_count=Subquery(student_counts)
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
    total_students = StudentLead.objects.count()
    total_cities = City.objects.filter(is_active=True).annotate(
        instructor_count=Count('instructors', filter=Q(instructors__is_visible=True))
    ).filter(instructor_count__gt=0).count()
    
    # Top states with students
    top_student_states = StudentLead.objects.values('state__code', 'state__name').annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    # Get all students with state coordinates for map (grouped by city name)
    students_with_location = StudentLead.objects.filter(
        city__isnull=False,
        state__latitude__isnull=False,
        state__longitude__isnull=False
    ).select_related('state', 'city').prefetch_related('categories')
    
    # Group students by city name (using state coordinates)
    from collections import defaultdict
    students_by_city = defaultdict(lambda: {
        'students': [],
        'city_name': '',
        'state_code': '',
        'state_name': '',
        'latitude': 0,
        'longitude': 0,
        'count': 0
    })
    
    for student in students_with_location:
        # Use city name as key for grouping
        city_key = f"{student.city.name}_{student.state.code}"
        city_data = students_by_city[city_key]
        
        # Set city info if not set (using state coordinates as cities don't have them)
        if not city_data['city_name']:
            city_data['city_name'] = student.city.name
            city_data['state_code'] = student.state.code
            city_data['state_name'] = student.state.name
            # Use state coordinates since City model doesn't have lat/lng
            city_data['latitude'] = float(student.state.latitude)
            city_data['longitude'] = float(student.state.longitude)
        
        # Get categories as comma-separated string
        categories_str = ', '.join([cat.code for cat in student.categories.all()]) if student.categories.exists() else 'N/A'
        
        city_data['students'].append({
            'id': student.id,
            'name': student.name,
            'category': categories_str,
            'has_theory': student.has_theory,
        })
        city_data['count'] += 1
    
    # Convert to list for JSON
    students_data = [
        {
            'city_name': data['city_name'],
            'state_code': data['state_code'],
            'state_name': data['state_name'],
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'count': data['count'],
            'students': data['students']
        }
        for data in students_by_city.values()
    ]
    
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
            'students': state.student_count or 0,
            'coordinates': coords
        })
    
    context = {
        'states': states,
        'states_json': json.dumps(states_data),
        'instructors_json': json.dumps(instructors_data),
        'students_json': json.dumps(students_data),
        'featured_instructors': featured_instructors,
        'total_instructors': total_instructors,
        'total_students': total_students,
        'total_cities': total_cities,
        'top_student_states': top_student_states,
        'banners': banners,
        'page_title': 'Cadastre-se como Instrutor - TREINACNH',
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


def city_students_view(request, state_code, city_name):
    """
    NOVO MODELO: Alunos veem instrutores (não o contrário).
    Esta view agora mostra INSTRUTORES para ALUNOS contatarem.
    """
    from marketplace.models import InstructorProfile, City, State
    from django.contrib import messages
    
    # Bloquear acesso de instrutores
    if request.user.is_authenticated:
        try:
            instructor_profile = request.user.instructor_profile
            messages.error(request, 'Instrutores não podem visualizar esta página. Aguarde os alunos entrarem em contato com você.')
            return redirect('marketplace:cities_list')
        except:
            pass  # User is not an instructor, continue
    
    # Get city
    try:
        state = State.objects.get(code=state_code.upper())
        city = City.objects.get(name__iexact=city_name, state=state)
    except (State.DoesNotExist, City.DoesNotExist):
        messages.error(request, 'Cidade não encontrada.')
        return redirect('core:home')
    
    # Get instructors from the city (VISIBLE and VERIFIED only for students)
    instructors = InstructorProfile.objects.filter(
        city=city,
        is_visible=True,
        is_verified=True
    ).select_related('user', 'user__profile', 'city', 'city__state').order_by('-created_at')
    
    # Check if user is logged in student
    is_student = request.user.is_authenticated and not hasattr(request.user, 'instructor_profile')
    
    context = {
        'city': city,
        'state': state,
        'instructors': instructors,
        'total_instructors': instructors.count(),
        'is_student': is_student,
        'is_authenticated': request.user.is_authenticated,
        'page_title': f'Instrutores em {city.name} - {state.code}',
    }
    
    return render(request, 'core/city_instructors.html', context)


def lcp_test_view(request):
    """Simple LCP test page without Bootstrap or external CSS"""
    return render(request, 'lcp_test.html')


def mobile_lcp_test_view(request):
    """Mobile LCP test page with optimized srcset"""
    return render(request, 'mobile_lcp_test.html')
