"""
API views for AJAX requests
"""
from django.http import JsonResponse
from .models import City


def get_cities_by_state(request, state_code):
    """
    API endpoint to get cities by state code.
    Returns JSON with cities list.
    """
    cities = City.objects.filter(
        state__code=state_code.upper(),
        is_active=True
    ).values('id', 'name').order_by('name')
    
    return JsonResponse({
        'cities': list(cities)
    })
