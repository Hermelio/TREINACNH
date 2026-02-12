"""
Update instructor coordinates from city geocache
This copies city coordinates to instructor profile so they have their own location
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile, CityGeoCache
from django.utils.text import slugify

instructors = InstructorProfile.objects.filter(is_visible=True).select_related('city', 'city__state')

updated = 0
skipped = 0
failed = 0

print(f"Processing {instructors.count()} instructors...")
print("="*80)

for instructor in instructors:
    # Skip if already has own coordinates
    if instructor.latitude and instructor.longitude:
        print(f"⚡ {instructor.user.get_full_name()} - Already has coordinates")
        skipped += 1
        continue
    
    # Get city coordinates
    city_key = f"{slugify(instructor.city.name)}|{instructor.city.state.code}"
    try:
        geo_cache = CityGeoCache.objects.get(city_key=city_key, geocoded=True)
        if geo_cache.latitude and geo_cache.longitude:
            instructor.latitude = geo_cache.latitude
            instructor.longitude = geo_cache.longitude
            instructor.save()
            print(f"✓ {instructor.user.get_full_name()} - Updated to {geo_cache.latitude}, {geo_cache.longitude}")
            updated += 1
        else:
            print(f"✗ {instructor.user.get_full_name()} - No coordinates in cache")
            failed += 1
    except CityGeoCache.DoesNotExist:
        print(f"✗ {instructor.user.get_full_name()} - City not in geocache")
        failed += 1

print("\n" + "="*80)
print(f"Updated: {updated}")
print(f"Already had coordinates: {skipped}")
print(f"Failed: {failed}")
print("="*80)
