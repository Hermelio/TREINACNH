"""
Views for marketplace app - listings, filters, and instructor profiles.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Prefetch
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from .models import State, City, InstructorProfile, Lead, CategoryCNH, StudentLead
from .forms import InstructorProfileForm, LeadForm, InstructorSearchForm, StudentRegistrationForm
from core.seo import build_seo


def cities_list_view(request):
    """
    Main cities page - list all states with cities and instructor counts.
    Shows "new instructors" section and interactive map with filtering.
    """
    from django.db.models import OuterRef, Subquery, Avg
    
    # Get instructor count per state
    instructor_counts = InstructorProfile.objects.filter(
        is_visible=True,
        city__state=OuterRef('pk')
    ).values('city__state').annotate(
        total=Count('id')
    ).values('total')
    
    states = State.objects.prefetch_related(
        Prefetch('cities', queryset=City.objects.filter(is_active=True))
    ).annotate(
        city_count=Count('cities', filter=Q(cities__is_active=True)),
        instructor_count=Subquery(instructor_counts)
    ).order_by('code')
    
    # Get ALL instructors (not just new ones)
    all_instructors = InstructorProfile.objects.filter(
        is_visible=True
    ).select_related('user', 'user__profile', 'city', 'city__state').prefetch_related('categories')
    
    # Apply filters from request
    search_name = request.GET.get('search_name', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    min_rating = request.GET.get('min_rating', '').strip()
    category = request.GET.get('category', '').strip()
    has_car = request.GET.get('has_car', '').strip()
    availability = request.GET.get('availability', '').strip()
    selected_state = request.GET.get('state', '').strip()
    selected_city = request.GET.get('city', '').strip()
    
    # Filter by name (search in first_name or last_name)
    if search_name:
        all_instructors = all_instructors.filter(
            Q(user__first_name__icontains=search_name) |
            Q(user__last_name__icontains=search_name)
        )
    
    # Filter by price range
    if min_price:
        try:
            all_instructors = all_instructors.filter(base_price_per_hour__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            all_instructors = all_instructors.filter(base_price_per_hour__lte=float(max_price))
        except ValueError:
            pass
    
    # Filter by minimum rating (requires review system - for now commented)
    # if min_rating:
    #     try:
    #         all_instructors = all_instructors.annotate(
    #             avg_rating=Avg('reviews__rating')
    #         ).filter(avg_rating__gte=float(min_rating))
    #     except ValueError:
    #         pass
    
    # Filter by CNH category
    if category and category in ['A', 'B', 'C', 'D', 'E']:
        all_instructors = all_instructors.filter(categories__code=category)
    
    # Filter by own car
    if has_car == '1':
        all_instructors = all_instructors.filter(has_own_car=True)
    elif has_car == '0':
        all_instructors = all_instructors.filter(has_own_car=False)
    
    # Filter by availability
    if availability == 'morning':
        all_instructors = all_instructors.filter(available_morning=True)
    elif availability == 'afternoon':
        all_instructors = all_instructors.filter(available_afternoon=True)
    elif availability == 'evening':
        all_instructors = all_instructors.filter(available_evening=True)
    
    # Filter by state
    if selected_state:
        all_instructors = all_instructors.filter(city__state__code=selected_state)
    
    # Filter by city
    if selected_city:
        try:
            all_instructors = all_instructors.filter(city__id=int(selected_city))
        except ValueError:
            pass
    
    # Order results
    all_instructors = all_instructors.order_by('-created_at')
    
    # New instructors (last 30 days) for highlights section
    from django.utils import timezone
    from datetime import timedelta
    new_instructors = all_instructors.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    )[:6]
    
    # Get all instructors with coordinates for map markers
    instructors_with_location = all_instructors.filter(
        latitude__isnull=False,
        longitude__isnull=False
    )
    
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
    import json
    states_data = []
    for state in states:
        coords = None
        if state.latitude and state.longitude:
            coords = [float(state.latitude), float(state.longitude)]
        
        states_data.append({
            'code': state.code,
            'name': state.name,
            'cities': state.city_count,
            'instructors': state.instructor_count or 0,
            'coordinates': coords
        })
    
    context = {
        'states': states,
        'states_json': json.dumps(states_data),
        'instructors_json': json.dumps(instructors_data),
        'all_instructors': all_instructors,
        'new_instructors': new_instructors,
        'page_title': 'Instrutores por Cidade',
        # Pass filter values back to template for maintaining state
        'search_name': search_name,
        'min_price': min_price,
        'max_price': max_price,
        'min_rating': min_rating,
        'selected_category': category,
        'selected_has_car': has_car,
        'selected_availability': availability,
        'selected_state': selected_state,
        'selected_city': selected_city,
        'all_states': states,  # For state dropdown
        'cnh_categories': list(
            CategoryCNH.objects.values_list('code', flat=True).order_by('code')
        ),
    }
    return render(request, 'marketplace/cities_list.html', context)


def city_instructors_list_view(request, state_code, city_slug):
    """
    List instructors in a specific city with filters.
    Main marketplace page.
    """
    city = get_object_or_404(City, slug=city_slug, state__code=state_code.upper(), is_active=True)
    
    # Base queryset
    instructors = InstructorProfile.objects.filter(
        city=city,
        is_visible=True
    ).select_related('user', 'user__profile', 'city', 'city__state').prefetch_related('categories')
    
    # Apply filters
    form = InstructorSearchForm(request.GET)
    if form.is_valid():
        gender = form.cleaned_data.get('gender')
        if gender:
            instructors = instructors.filter(gender=gender)
        
        category = form.cleaned_data.get('category')
        if category:
            instructors = instructors.filter(categories=category)
        
        has_own_car = form.cleaned_data.get('has_own_car')
        if has_own_car == 'yes':
            instructors = instructors.filter(has_own_car=True)
        elif has_own_car == 'no':
            instructors = instructors.filter(has_own_car=False)
        
        availability = form.cleaned_data.get('availability')
        if availability == 'morning':
            instructors = instructors.filter(available_morning=True)
        elif availability == 'afternoon':
            instructors = instructors.filter(available_afternoon=True)
        elif availability == 'evening':
            instructors = instructors.filter(available_evening=True)
        
        verified_only = form.cleaned_data.get('verified_only')
        if verified_only:
            instructors = instructors.filter(is_verified=True)
    
    # Ordering: verified and highlighted first, then newest
    instructors = instructors.order_by('-is_verified', '-created_at')
    
    # Pagination
    paginator = Paginator(instructors, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'city': city,
        'page_obj': page_obj,
        'form': form,
        'total_instructors': instructors.count(),
        'page_title': f'Instrutores em {city.name}/{city.state.code}',
    }
    return render(request, 'marketplace/city_instructors_list.html', context)


def instructor_detail_view(request, pk):
    """
    Instructor profile detail page.
    Shows bio, categories, availability, reviews, and contact options.
    """
    instructor = get_object_or_404(
        InstructorProfile.objects.select_related('user', 'user__profile', 'city', 'city__state').prefetch_related('categories'),
        pk=pk
    )
    
    # Only show if visible or user is the instructor
    if not instructor.is_visible and (not request.user.is_authenticated or request.user != instructor.user):
        messages.error(request, 'Este perfil não está disponível.')
        return redirect('marketplace:cities_list')
    
    # Get reviews
    from reviews.models import Review
    reviews = Review.objects.filter(
        instructor=instructor,
        status='PUBLISHED'
    ).select_related('author_user').order_by('-created_at')[:10]
    
    # Average rating
    from django.db.models import Avg
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    # WhatsApp message
    whatsapp_link = instructor.get_whatsapp_link()

    # Flag so the template can hide direct-contact buttons for students who haven't
    # finished their profile yet (same rule as the lead_create_view guard).
    student_data_incomplete = (
        request.user.is_authenticated
        and hasattr(request.user, 'profile')
        and request.user.profile.is_student
        and not request.user.profile.is_student_data_complete
    )

    # Dynamic SEO: instructor name + city in title, bio as description
    full_name = instructor.user.get_full_name()
    city_name = instructor.city.name if instructor.city else ''
    seo = build_seo(
        title=f'Instrutor {full_name} em {city_name} | TreinaCNH',
        description=(
            instructor.bio
            or f'Instrutor de trânsito autônomo credenciado em {city_name}. '
               f'Aulas de direção particular. Veja avaliações e agende na TreinaCNH.'
        ),
    )

    context = {
        'instructor': instructor,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'whatsapp_link': whatsapp_link,
        'student_data_incomplete': student_data_incomplete,
        **seo,
    }
    return render(request, 'marketplace/instructor_detail.html', context)


@require_http_methods(["GET", "POST"])
def lead_create_view(request, instructor_pk):
    """
    Create a lead/contact request for an instructor.
    Can be used by logged-in users or anonymous visitors.
    """
    # Guard: authenticated students must have complete profile data
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile and profile.is_student and not profile.is_student_data_complete:
            from django.urls import reverse
            from urllib.parse import urlencode
            next_url = request.get_full_path()
            return redirect(
                reverse('accounts:complete_student_data') + '?' + urlencode({'next': next_url})
            )
    instructor = get_object_or_404(InstructorProfile, pk=instructor_pk, is_visible=True)
    
    if request.method == 'POST':
        form = LeadForm(request.POST, user=request.user)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.instructor = instructor
            lead.city = instructor.city
            
            # Associate with user if logged in
            if request.user.is_authenticated:
                lead.student_user = request.user
            
            # Save IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                lead.ip_address = x_forwarded_for.split(',')[0]
            else:
                lead.ip_address = request.META.get('REMOTE_ADDR')
            
            lead.save()
            
            messages.success(request, f'Solicitação enviada para {instructor.user.get_full_name()}! O instrutor entrará em contato em breve.')
            return redirect('marketplace:instructor_detail', pk=instructor.pk)
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = LeadForm(user=request.user)
    
    context = {
        'form': form,
        'instructor': instructor,
        'page_title': f'Solicitar Contato - {instructor.user.get_full_name()}',
    }
    return render(request, 'marketplace/lead_create.html', context)


@login_required
def instructor_profile_edit_view(request):
    """
    Edit instructor profile (for instructors only).
    Creates profile if doesn't exist.
    """
    # Check if user is instructor
    if not request.user.profile.is_instructor:
        messages.error(request, 'Apenas instrutores podem acessar esta página.')
        return redirect('accounts:dashboard')
    
    # Get or create instructor profile
    try:
        instructor_profile = InstructorProfile.objects.get(user=request.user)
    except InstructorProfile.DoesNotExist:
        instructor_profile = None
    
    if request.method == 'POST':
        form = InstructorProfileForm(request.POST, instance=instructor_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            if not profile.user_id:
                profile.user = request.user
            profile.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Try to geocode address automatically
            from .geocoding import geocode_instructor_profile
            try:
                if geocode_instructor_profile(profile):
                    messages.success(request, 'Perfil atualizado com sucesso! Suas coordenadas foram calculadas automaticamente.')
                else:
                    messages.success(request, 'Perfil atualizado com sucesso!')
                    if not profile.latitude or not profile.longitude:
                        messages.info(request, 'Não foi possível calcular suas coordenadas automaticamente. Verifique seu endereço.')
            except Exception as e:
                messages.success(request, 'Perfil atualizado com sucesso!')
                messages.warning(request, f'Erro ao calcular coordenadas: {str(e)}')
            
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        # Pre-fill city from user profile if creating new instructor profile
        initial_data = {}
        if not instructor_profile and request.user.profile.preferred_city:
            initial_data['city'] = request.user.profile.preferred_city
        
        form = InstructorProfileForm(instance=instructor_profile, initial=initial_data)
    
    # Calculate completion score
    completion_score = instructor_profile.profile_completion_score if instructor_profile else 0
    
    context = {
        'form': form,
        'instructor_profile': instructor_profile,
        'completion_score': completion_score,
        'page_title': 'Editar Perfil de Instrutor',
    }
    return render(request, 'marketplace/instructor_profile_edit.html', context)


@login_required
def my_leads_view(request):
    """View leads received (for instructors) or sent (for students)"""
    profile = request.user.profile
    
    if profile.is_instructor:
        # Show leads received
        try:
            instructor_profile = InstructorProfile.objects.get(user=request.user)
            leads = Lead.objects.filter(instructor=instructor_profile).select_related('city').order_by('-created_at')
            
            # Filter by status
            status_filter = request.GET.get('status')
            if status_filter:
                leads = leads.filter(status=status_filter)
            
            context = {
                'leads': leads,
                'is_instructor': True,
                'page_title': 'Leads Recebidos',
            }
        except InstructorProfile.DoesNotExist:
            messages.warning(request, 'Complete seu perfil de instrutor primeiro.')
            return redirect('marketplace:instructor_profile_edit')
    else:
        # Show leads sent
        leads = Lead.objects.filter(student_user=request.user).select_related('instructor', 'instructor__user', 'city').order_by('-created_at')
        context = {
            'leads': leads,
            'is_instructor': False,
            'page_title': 'Minhas Solicitações',
        }
    
    return render(request, 'marketplace/my_leads.html', context)


@login_required
@require_http_methods(["POST"])
def lead_update_status_view(request, lead_pk):
    """Update lead status (instructor only)"""
    lead = get_object_or_404(Lead, pk=lead_pk)
    
    # Check permission
    if not hasattr(request.user, 'instructor_profile') or lead.instructor != request.user.instructor_profile:
        messages.error(request, 'Você não tem permissão para modificar este lead.')
        return redirect('marketplace:my_leads')
    
    new_status = request.POST.get('status')
    if new_status in dict(Lead._meta.get_field('status').choices):
        lead.status = new_status
        lead.save()
        messages.success(request, 'Status atualizado com sucesso!')
    else:
        messages.error(request, 'Status inválido.')
    
    return redirect('marketplace:my_leads')


def student_register_view(request):
    """Student registration form"""
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            
            # Get selected categories before saving
            categories = form.cleaned_data.get('categories')
            
            # Save student
            student.save()
            
            # Add categories (ManyToMany relationship)
            if categories:
                student.categories.set(categories)
            
            # Success message
            messages.success(
                request, 
                f'Cadastro realizado com sucesso, {student.name.split()[0]}! '
                'Entraremos em contato em breve quando houver instrutores disponíveis na sua região.'
            )
            
            # Redirect to success page or home
            return redirect('core:home')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = StudentRegistrationForm()
    
    # Get all states for the form
    states = State.objects.all().order_by('code')
    categories = CategoryCNH.objects.all().order_by('code')
    
    context = {
        'form': form,
        'states': states,
        'categories': categories,
        'seo_title': 'Cadastro de Aluno | TreinaCNH',
        'seo_description': 'Cadastre-se como aluno na TreinaCNH e seja encontrado por instrutores de trânsito autônomos credenciados na sua cidade.',
    }
    return render(request, 'marketplace/student_register.html', context)


def get_cities_by_state(request):
    """AJAX endpoint to get cities for a given state"""
    from django.http import JsonResponse
    
    state_id = request.GET.get('state_id')
    if not state_id:
        return JsonResponse({'cities': []})
    
    cities = City.objects.filter(state_id=state_id, is_active=True).values('id', 'name').order_by('name')
    return JsonResponse({'cities': list(cities)})
