"""
Geocoding service with cache for city coordinates
"""
import time
import logging
from decimal import Decimal
from typing import Tuple, Optional
import requests
from django.conf import settings
from .models import CityGeoCache

logger = logging.getLogger(__name__)


class GeocodingService:
    """Service for geocoding cities with cache"""
    
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    USER_AGENT = "TreinaCNH/1.0"
    RATE_LIMIT_DELAY = 1.5  # seconds between requests (Nominatim requires 1 req/sec max)
    
    @staticmethod
    def get_city_latlng(city_name: str, state_code: str) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """
        Get latitude and longitude for a city, using cache when available.
        
        Args:
            city_name: Name of the city
            state_code: State code (UF)
            
        Returns:
            Tuple of (latitude, longitude) or (None, None) if not found
        """
        # Normalize city key
        city_key = CityGeoCache.normalize_city_key(city_name, state_code)
        
        # Check cache first
        try:
            cache_entry = CityGeoCache.objects.get(city_key=city_key)
            
            # If already geocoded successfully, return coordinates
            if cache_entry.geocoded and cache_entry.latitude and cache_entry.longitude:
                return cache_entry.latitude, cache_entry.longitude
            
            # If failed multiple times, don't retry
            if cache_entry.failed and cache_entry.attempts >= 3:
                logger.warning(f"Geocoding failed multiple times for {city_name}/{state_code}")
                return None, None
                
        except CityGeoCache.DoesNotExist:
            # Create new cache entry
            cache_entry = CityGeoCache.objects.create(
                city_key=city_key,
                city_name=city_name,
                state_code=state_code,
                geocoded=False
            )
        
        # Attempt geocoding
        try:
            lat, lng = GeocodingService._geocode_nominatim(city_name, state_code)
            
            if lat and lng:
                # Update cache with success
                cache_entry.latitude = lat
                cache_entry.longitude = lng
                cache_entry.geocoded = True
                cache_entry.failed = False
                cache_entry.provider = 'nominatim'
                cache_entry.attempts += 1
                cache_entry.save()
                
                logger.info(f"Successfully geocoded {city_name}/{state_code}: {lat}, {lng}")
                return lat, lng
            else:
                # Mark as failed
                cache_entry.failed = True
                cache_entry.attempts += 1
                cache_entry.save()
                
                logger.warning(f"Failed to geocode {city_name}/{state_code}")
                return None, None
                
        except Exception as e:
            logger.error(f"Error geocoding {city_name}/{state_code}: {str(e)}")
            cache_entry.failed = True
            cache_entry.attempts += 1
            cache_entry.save()
            return None, None
    
    @staticmethod
    def _geocode_nominatim(city_name: str, state_code: str) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """
        Geocode using Nominatim (OpenStreetMap)
        
        Args:
            city_name: Name of the city
            state_code: State code (UF)
            
        Returns:
            Tuple of (latitude, longitude) or (None, None) if not found
        """
        # Respect rate limit
        time.sleep(GeocodingService.RATE_LIMIT_DELAY)
        
        # Build query
        query = f"{city_name}, {state_code}, Brasil"
        
        params = {
            'q': query,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'br',
            'addressdetails': 1
        }
        
        headers = {
            'User-Agent': GeocodingService.USER_AGENT
        }
        
        try:
            response = requests.get(
                GeocodingService.NOMINATIM_URL,
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                lat = Decimal(str(result['lat']))
                lng = Decimal(str(result['lon']))
                
                return lat, lng
            else:
                return None, None
                
        except requests.RequestException as e:
            logger.error(f"Nominatim request failed for {query}: {str(e)}")
            return None, None
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing Nominatim response for {query}: {str(e)}")
            return None, None
    
    @staticmethod
    def batch_geocode_cities(city_state_pairs: list, delay: float = 1.5) -> dict:
        """
        Geocode multiple cities in batch with rate limiting
        
        Args:
            city_state_pairs: List of tuples (city_name, state_code)
            delay: Delay between requests in seconds
            
        Returns:
            Dict with stats: {'success': int, 'failed': int, 'cached': int}
        """
        stats = {'success': 0, 'failed': 0, 'cached': 0, 'total': len(city_state_pairs)}
        
        for i, (city_name, state_code) in enumerate(city_state_pairs, 1):
            logger.info(f"Processing {i}/{stats['total']}: {city_name}/{state_code}")
            
            # Check if already in cache
            city_key = CityGeoCache.normalize_city_key(city_name, state_code)
            try:
                cache_entry = CityGeoCache.objects.get(city_key=city_key)
                if cache_entry.geocoded:
                    stats['cached'] += 1
                    logger.info(f"  → Already cached")
                    continue
            except CityGeoCache.DoesNotExist:
                pass
            
            # Geocode
            lat, lng = GeocodingService.get_city_latlng(city_name, state_code)
            
            if lat and lng:
                stats['success'] += 1
                logger.info(f"  → Success: {lat}, {lng}")
            else:
                stats['failed'] += 1
                logger.warning(f"  → Failed")
            
            # Rate limiting (except for last item)
            if i < stats['total']:
                time.sleep(delay)
        
        return stats
