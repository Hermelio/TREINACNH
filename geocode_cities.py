#!/usr/bin/env python
"""
Script to pre-geocode all cities from StudentLead records.
Run this to populate the CityGeoCache before users access the map.

Usage:
    python geocode_cities.py
    python geocode_cities.py --retry-failed  # Retry previously failed cities
"""
import os
import sys
import django
import argparse

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import StudentLead, CityGeoCache
from marketplace.geocoding_service import GeocodingService
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_unique_cities(retry_failed=False):
    """Get unique city/state combinations from StudentLead"""
    students = StudentLead.objects.filter(
        city__isnull=False,
        state__isnull=False
    ).select_related('city', 'state').distinct()
    
    # Get unique combinations
    city_state_pairs = set()
    for student in students:
        city_state_pairs.add((student.city.name, student.state.code))
    
    # Filter out already geocoded (unless retry_failed is True)
    if not retry_failed:
        to_geocode = []
        for city_name, state_code in city_state_pairs:
            city_key = CityGeoCache.normalize_city_key(city_name, state_code)
            try:
                cache = CityGeoCache.objects.get(city_key=city_key)
                if not cache.geocoded:
                    to_geocode.append((city_name, state_code))
            except CityGeoCache.DoesNotExist:
                to_geocode.append((city_name, state_code))
        return to_geocode
    else:
        # Retry all including failed ones
        return list(city_state_pairs)


def show_stats():
    """Show current geocoding statistics"""
    from django.db.models import Count, Q
    
    total_cache = CityGeoCache.objects.count()
    geocoded = CityGeoCache.objects.filter(geocoded=True).count()
    failed = CityGeoCache.objects.filter(failed=True).count()
    pending = total_cache - geocoded - failed
    
    # Get student counts by city
    students_by_city = StudentLead.objects.filter(
        city__isnull=False,
        state__isnull=False
    ).values('city__name', 'state__code').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    print("\n" + "="*60)
    print("GEOCODING STATISTICS")
    print("="*60)
    print(f"Total cached cities: {total_cache}")
    print(f"  ✓ Successfully geocoded: {geocoded}")
    print(f"  ✗ Failed: {failed}")
    print(f"  ? Pending: {pending}")
    print()
    
    print("TOP 10 CITIES BY STUDENT COUNT:")
    print("-" * 60)
    for item in students_by_city:
        city_name = item['city__name']
        state_code = item['state__code']
        count = item['count']
        
        # Check if geocoded
        city_key = CityGeoCache.normalize_city_key(city_name, state_code)
        try:
            cache = CityGeoCache.objects.get(city_key=city_key)
            status = '✓' if cache.geocoded else ('✗' if cache.failed else '?')
        except CityGeoCache.DoesNotExist:
            status = '?'
        
        print(f"  {status} {city_name}/{state_code}: {count} alunos")
    
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Geocode cities from StudentLead records')
    parser.add_argument('--retry-failed', action='store_true', help='Retry previously failed cities')
    parser.add_argument('--stats-only', action='store_true', help='Show statistics only, no geocoding')
    args = parser.parse_args()
    
    if args.stats_only:
        show_stats()
        return
    
    logger.info("Starting city geocoding process...")
    
    # Get cities to geocode
    cities_to_geocode = get_unique_cities(retry_failed=args.retry_failed)
    
    if not cities_to_geocode:
        logger.info("All cities are already geocoded!")
        show_stats()
        return
    
    logger.info(f"Found {len(cities_to_geocode)} cities to geocode")
    
    # Ask for confirmation
    response = input(f"\nThis will make ~{len(cities_to_geocode)} API requests. Continue? (y/n): ")
    if response.lower() != 'y':
        logger.info("Aborted by user")
        return
    
    # Batch geocode
    logger.info("Starting batch geocoding...")
    stats = GeocodingService.batch_geocode_cities(cities_to_geocode, delay=1.5)
    
    logger.info("\n" + "="*60)
    logger.info("GEOCODING COMPLETED")
    logger.info("="*60)
    logger.info(f"Total processed: {stats['total']}")
    logger.info(f"  ✓ Success: {stats['success']}")
    logger.info(f"  ✗ Failed: {stats['failed']}")
    logger.info(f"  ⚡ Cached (skipped): {stats['cached']}")
    logger.info("="*60)
    
    # Show final stats
    show_stats()


if __name__ == '__main__':
    main()
