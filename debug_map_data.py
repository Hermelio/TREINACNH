"""
Debug instructors map data
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile, CityGeoCache
from django.utils.text import slugify
import json

# Get instructors like the view does
instructors_qs = InstructorProfile.objects.filter(
    is_visible=True,
).select_related(
    'user', 
    'user__profile', 
    'city', 
    'city__state'
).prefetch_related('categories')

print(f"Total visible instructors: {instructors_qs.count()}")
print("\nInstructors that will appear on map:")
print("="*80)

instructors_json = []
for instructor in instructors_qs:
    lat = None
    lon = None
    
    # Try instructor coordinates first
    if instructor.latitude and instructor.longitude:
        lat = float(instructor.latitude)
        lon = float(instructor.longitude)
        source = "own"
    else:
        # Fallback to city coordinates from geocache
        city_key = f"{slugify(instructor.city.name)}|{instructor.city.state.code}"
        try:
            geo_cache = CityGeoCache.objects.get(city_key=city_key, geocoded=True)
            if geo_cache.latitude and geo_cache.longitude:
                lat = float(geo_cache.latitude)
                lon = float(geo_cache.longitude)
                source = "city"
        except CityGeoCache.DoesNotExist:
            source = "none"
    
    if lat and lon:
        instructors_json.append({
            'id': instructor.id,
            'name': instructor.user.get_full_name(),
            'latitude': lat,
            'longitude': lon,
            'neighborhood': instructor.address_neighborhood,
            'city': str(instructor.city),
            'is_verified': instructor.is_verified,
            'type': 'instructor',
        })
        print(f"✓ {instructor.user.get_full_name()} - {instructor.city}")
        print(f"  Coords: {lat}, {lon} (from {source})")
    else:
        print(f"✗ {instructor.user.get_full_name()} - {instructor.city}")
        print(f"  NO COORDINATES")

print("\n" + "="*80)
print(f"\nTotal with coordinates: {len(instructors_json)}")
print("\nJSON that will be sent to map:")
print(json.dumps(instructors_json, indent=2))
