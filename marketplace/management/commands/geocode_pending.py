"""
Management command to geocode pending cities.
Run this via cron job to automatically geocode new cities.

Usage:
    python manage.py geocode_pending
    python manage.py geocode_pending --all  # Geocode all cities, including already processed
"""
from django.core.management.base import BaseCommand
from marketplace.models import CityGeoCache, StudentLead
from marketplace.geocoding_service import GeocodingService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Geocode pending cities that are not yet processed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Geocode all cities, including already processed',
        )
        parser.add_argument(
            '--retry-failed',
            action='store_true',
            help='Retry cities that previously failed',
        )

    def handle(self, *args, **options):
        self.stdout.write('Checking for cities to geocode...')
        
        # Get unique cities from StudentLead
        students = StudentLead.objects.filter(
            city__isnull=False,
            state__isnull=False
        ).select_related('city', 'state').distinct()
        
        city_state_pairs = set()
        for student in students:
            city_state_pairs.add((student.city.name, student.state.code))
        
        self.stdout.write(f'Found {len(city_state_pairs)} unique cities in StudentLead records')
        
        # Filter based on options
        to_geocode = []
        for city_name, state_code in city_state_pairs:
            city_key = CityGeoCache.normalize_city_key(city_name, state_code)
            
            try:
                cache = CityGeoCache.objects.get(city_key=city_key)
                
                if options['all']:
                    # Geocode all
                    to_geocode.append((city_name, state_code))
                elif options['retry_failed'] and cache.failed:
                    # Retry failed
                    to_geocode.append((city_name, state_code))
                elif not cache.geocoded and not cache.failed:
                    # Only pending
                    to_geocode.append((city_name, state_code))
                    
            except CityGeoCache.DoesNotExist:
                # Not in cache yet
                to_geocode.append((city_name, state_code))
        
        if not to_geocode:
            self.stdout.write(self.style.SUCCESS('✓ All cities are already geocoded!'))
            return
        
        self.stdout.write(f'Will geocode {len(to_geocode)} cities...')
        
        # Geocode
        stats = GeocodingService.batch_geocode_cities(to_geocode, delay=1.5)
        
        # Report results
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('GEOCODING COMPLETED'))
        self.stdout.write('='*60)
        self.stdout.write(f'Total processed: {stats["total"]}')
        self.stdout.write(self.style.SUCCESS(f'  ✓ Success: {stats["success"]}'))
        self.stdout.write(self.style.ERROR(f'  ✗ Failed: {stats["failed"]}'))
        self.stdout.write(f'  ⚡ Cached (skipped): {stats["cached"]}')
        self.stdout.write('='*60)
