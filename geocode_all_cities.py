"""
Script to geocode ALL cities in the database, not just those with students.
Uses Nominatim (OpenStreetMap) API.
"""
import os
import sys
import django
import time
from urllib.parse import quote
import requests

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import City, CityGeoCache
from django.utils.text import slugify

def geocode_city(city_name, state_code):
    """
    Geocode a city using Nominatim API
    Returns (latitude, longitude) or (None, None) if not found
    """
    query = f"{city_name}, {state_code}, Brazil"
    url = f"https://nominatim.openstreetmap.org/search?q={quote(query)}&format=json&limit=1"
    
    headers = {
        'User-Agent': 'TreinaCNH/1.0 (contact@treinacnh.com.br)'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return lat, lon
        else:
            return None, None
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None, None

def geocode_all_cities_from_db():
    """Geocode all cities from City model that don't have coordinates"""
    cities = City.objects.all().select_related('state')
    
    total = cities.count()
    geocoded_count = 0
    failed_count = 0
    skipped_count = 0
    
    print(f"Found {total} cities in database")
    print("Note: Nominatim has rate limit of 1 request/second")
    print("="*60)
    
    for i, city in enumerate(cities, 1):
        city_key = f"{slugify(city.name)}|{city.state.code}"
        
        # Check if already geocoded
        try:
            cache = CityGeoCache.objects.get(city_key=city_key)
            if cache.geocoded and cache.latitude and cache.longitude:
                if cache.latitude != 0.0 and cache.longitude != 0.0:
                    skipped_count += 1
                    if i % 50 == 0:
                        print(f"[{i}/{total}] Skipping already geocoded cities...")
                    continue
        except CityGeoCache.DoesNotExist:
            pass
        
        print(f"\n[{i}/{total}] Geocoding: {city.name}/{city.state.code}")
        
        lat, lon = geocode_city(city.name, city.state.code)
        
        if lat is not None and lon is not None:
            CityGeoCache.objects.update_or_create(
                city_key=city_key,
                defaults={
                    'city_name': city.name,
                    'state_code': city.state.code,
                    'latitude': lat,
                    'longitude': lon,
                    'provider': 'nominatim',
                    'geocoded': True
                }
            )
            print(f"  ✓ Success: {lat}, {lon}")
            geocoded_count += 1
        else:
            print(f"  ⚠️  Not found - keeping coordinates as 0,0")
            CityGeoCache.objects.update_or_create(
                city_key=city_key,
                defaults={
                    'city_name': city.name,
                    'state_code': city.state.code,
                    'latitude': 0.0,
                    'longitude': 0.0,
                    'provider': 'nominatim',
                    'geocoded': False
                }
            )
            failed_count += 1
        
        # Respect Nominatim rate limit (1 request per second)
        time.sleep(1.1)
    
    print("\n" + "="*60)
    print("Geocoding completed!")
    print(f"Successfully geocoded: {geocoded_count}")
    print(f"Already had coordinates: {skipped_count}")
    print(f"Failed to geocode: {failed_count}")
    print("="*60)
    
    # Show final stats
    total_cache = CityGeoCache.objects.count()
    geocoded_total = CityGeoCache.objects.filter(geocoded=True).count()
    pending = CityGeoCache.objects.filter(geocoded=False).count()
    
    print("\nFINAL STATISTICS:")
    print(f"Total cities in cache: {total_cache}")
    print(f"  ✓ Successfully geocoded: {geocoded_total}")
    print(f"  ? Pending/Failed: {pending}")
    print("="*60)

if __name__ == '__main__':
    geocode_all_cities_from_db()
