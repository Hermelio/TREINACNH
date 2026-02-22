"""
API views for AJAX requests
"""
from django.http import JsonResponse
from django.db.models import Count
from .models import City, CityGeoCache, StudentLead
import logging

logger = logging.getLogger(__name__)


def get_cities_by_state(request, state_code):
    """
    API endpoint to get cities by state code.
    Returns JSON with cities list for all cities (not only is_active),
    so student dropdowns show every Brazilian municipality.
    """
    cities = City.objects.filter(
        state__code=state_code.upper()
    ).values('id', 'name').order_by('name')
    
    return JsonResponse({
        'cities': list(cities)
    })


def get_map_cities(request):
    """
    API endpoint for map visualization.
    Returns aggregated student data by city with coordinates.
    
    Returns JSON:
    {
        "cities": [
            {
                "city": "São Paulo",
                "uf": "SP",
                "lat": -23.5505,
                "lng": -46.6333,
                "count": 42,
                "categories": {"A": 15, "B": 30},
                "with_theory": 25
            },
            ...
        ],
        "stats": {
            "total_cities": 50,
            "total_students": 500,
            "cities_without_coords": 5
        }
    }
    """
    from collections import defaultdict
    
    # Get all students with city and state
    students = StudentLead.objects.filter(
        city__isnull=False,
        state__isnull=False
    ).select_related('city', 'state').prefetch_related('categories')
    
    # Group by city
    cities_data = defaultdict(lambda: {
        'city': '',
        'uf': '',
        'lat': None,
        'lng': None,
        'count': 0,
        'categories': defaultdict(int),
        'with_theory': 0,
        'students': []
    })
    
    for student in students:
        # Normalize city key
        city_key = CityGeoCache.normalize_city_key(student.city.name, student.state.code)
        city_data = cities_data[city_key]
        
        # Set city info
        if not city_data['city']:
            city_data['city'] = student.city.name
            city_data['uf'] = student.state.code
            
            # Get coordinates from cache
            try:
                cache = CityGeoCache.objects.get(city_key=city_key)
                if cache.geocoded and cache.latitude and cache.longitude:
                    city_data['lat'] = float(cache.latitude)
                    city_data['lng'] = float(cache.longitude)
            except CityGeoCache.DoesNotExist:
                logger.warning(f"No geocode cache for {student.city.name}/{student.state.code}")
        
        # Count student
        city_data['count'] += 1
        
        # Count categories
        for cat in student.categories.all():
            city_data['categories'][cat.code] += 1
        
        # Count theory
        if student.has_theory:
            city_data['with_theory'] += 1
    
    # Convert to list and filter cities without coordinates
    cities_list = []
    cities_without_coords = 0
    
    for city_data in cities_data.values():
        if city_data['lat'] and city_data['lng']:
            # Convert categories defaultdict to regular dict
            city_data['categories'] = dict(city_data['categories'])
            # Remove students list (not needed in response)
            del city_data['students']
            cities_list.append(city_data)
        else:
            cities_without_coords += 1
            logger.warning(f"City without coordinates: {city_data['city']}/{city_data['uf']}")
    
    # Calculate stats
    total_students = sum(c['count'] for c in cities_list)
    
    stats = {
        'total_cities': len(cities_list),
        'total_students': total_students,
        'cities_without_coords': cities_without_coords
    }
    
    return JsonResponse({
        'cities': cities_list,
        'stats': stats
    })
