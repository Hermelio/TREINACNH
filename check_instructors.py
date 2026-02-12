"""
Check instructor status in database
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile, CityGeoCache
from django.utils.text import slugify

instructors = InstructorProfile.objects.all().select_related('user', 'city', 'city__state')

print(f"Total instructors: {instructors.count()}")
print("\nInstructor Status:")
print("="*80)

for instructor in instructors:
    # Check coordinates
    has_own_coords = bool(instructor.latitude and instructor.longitude)
    
    # Check city coordinates
    city_key = f"{slugify(instructor.city.name)}|{instructor.city.state.code}"
    try:
        geo_cache = CityGeoCache.objects.get(city_key=city_key)
        has_city_coords = geo_cache.geocoded and geo_cache.latitude and geo_cache.longitude
        city_coords = f"{geo_cache.latitude}, {geo_cache.longitude}" if has_city_coords else "None"
    except CityGeoCache.DoesNotExist:
        has_city_coords = False
        city_coords = "No cache"
    
    status = []
    if instructor.is_visible:
        status.append("✓ Visible")
    else:
        status.append("✗ Hidden")
    
    if instructor.is_verified:
        status.append("✓ Verified")
    else:
        status.append("✗ Not Verified")
    
    if has_own_coords:
        status.append(f"✓ Own coords: {instructor.latitude}, {instructor.longitude}")
    elif has_city_coords:
        status.append(f"⚡ City coords: {city_coords}")
    else:
        status.append("✗ No coords")
    
    print(f"{instructor.user.get_full_name()} - {instructor.city}")
    print(f"  {' | '.join(status)}")

print("\n" + "="*80)
print(f"\nVisible & Verified: {instructors.filter(is_visible=True, is_verified=True).count()}")
print(f"Visible only: {instructors.filter(is_visible=True).count()}")
print(f"Verified only: {instructors.filter(is_verified=True).count()}")
