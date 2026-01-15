"""
View for instructors map with filters and student leads count
"""
import json
from django.shortcuts import render
from django.db.models import Q, Avg, Count
from .models import State, InstructorProfile, CategoryCNH, StudentLead


def instructors_map_view(request):
    """
    Interactive map view showing instructors and student leads count by state.
    This helps instructors see where there's demand.
    """
    # Get filter parameters
    state_code = request.GET.get('state', '').upper()
    category_code = request.GET.get('category', '')
    gender = request.GET.get('gender', '')
    
    # Base queryset - only verified and visible instructors with coordinates
    instructors_qs = InstructorProfile.objects.filter(
        is_visible=True,
        is_verified=True,
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related(
        'user', 
        'user__profile', 
        'city', 
        'city__state'
    ).prefetch_related('categories')
    
    # Apply filters
    if state_code:
        instructors_qs = instructors_qs.filter(city__state__code=state_code)
    
    if category_code:
        instructors_qs = instructors_qs.filter(categories__code=category_code)
    
    if gender:
        instructors_qs = instructors_qs.filter(gender=gender)
    
    # Get instructors (average_rating and total_reviews are now model fields, not annotations)
    instructors = instructors_qs.annotate(
        review_count=Count('reviews', filter=Q(reviews__status='PUBLISHED'))
    ).order_by('-created_at')
    
    # Prepare JSON data for map markers
    instructors_json = []
    for instructor in instructors:
        instructors_json.append({
            'id': instructor.id,
            'name': instructor.user.get_full_name(),
            'latitude': float(instructor.latitude) if instructor.latitude else None,
            'longitude': float(instructor.longitude) if instructor.longitude else None,
            'neighborhood': instructor.address_neighborhood,
            'city': str(instructor.city),
            'is_verified': instructor.is_verified,
        })
    
    # Get student leads count by state
    states_with_leads = State.objects.annotate(
        student_count=Count('student_leads'),
        waiting_students=Count('student_leads', filter=Q(student_leads__notified_about_instructor=False))
    ).filter(student_count__gt=0).order_by('code')
    
    # Prepare state statistics for display
    state_stats = []
    for state in states_with_leads:
        instructors_in_state = InstructorProfile.objects.filter(
            city__state=state,
            is_visible=True,
            is_verified=True
        ).count()
        
        state_stats.append({
            'code': state.code,
            'name': state.name,
            'student_count': state.student_count,
            'waiting_students': state.waiting_students,
            'instructor_count': instructors_in_state,
            'latitude': float(state.latitude) if state.latitude else None,
            'longitude': float(state.longitude) if state.longitude else None,
        })
    
    # Get all states and categories for filters
    states = State.objects.all().order_by('code')
    categories = CategoryCNH.objects.all().order_by('code')
    
    # Get current state if filtered
    current_state = None
    if state_code:
        try:
            current_state = State.objects.get(code=state_code)
        except State.DoesNotExist:
            pass
    
    # Total statistics
    total_students = StudentLead.objects.count()
    total_waiting = StudentLead.objects.filter(notified_about_instructor=False).count()
    
    context = {
        'instructors': instructors,
        'instructors_json': json.dumps(instructors_json),
        'instructors_count': instructors.count(),
        'state_stats': state_stats,
        'state_stats_json': json.dumps(state_stats),
        'total_students': total_students,
        'total_waiting': total_waiting,
        'states': states,
        'categories': categories,
        'current_state': current_state,
        'current_state_code': state_code,
        'selected_category': category_code,
        'selected_gender': gender,
        'page_title': 'Mapa de Instrutores e Alunos',
    }
    
    return render(request, 'marketplace/instructors_map.html', context)
