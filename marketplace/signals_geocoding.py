"""
Signals for automatic geocoding when students or instructors are created/updated
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StudentLead, InstructorProfile, CityGeoCache
from .geocoding_service import GeocodingService
import logging
import threading

logger = logging.getLogger(__name__)


def geocode_async(city_name, state_code):
    """
    Geocode a city in a background thread to avoid blocking the request.
    """
    try:
        logger.info(f"Auto-geocoding: {city_name}/{state_code}")
        lat, lng = GeocodingService.get_city_latlng(city_name, state_code)
        if lat and lng:
            logger.info(f"Auto-geocoded successfully: {city_name}/{state_code} -> {lat}, {lng}")
        else:
            logger.warning(f"Auto-geocoding failed: {city_name}/{state_code}")
    except Exception as e:
        logger.error(f"Error in auto-geocoding {city_name}/{state_code}: {str(e)}")


@receiver(post_save, sender=StudentLead)
def auto_geocode_student_city(sender, instance, created, **kwargs):
    """
    Automatically geocode city when a new StudentLead is created.
    """
    # Only process if has city and state
    if not instance.city or not instance.state:
        return
    
    city_name = instance.city.name
    state_code = instance.state.code
    
    # Check if already geocoded
    city_key = CityGeoCache.normalize_city_key(city_name, state_code)
    try:
        cache = CityGeoCache.objects.get(city_key=city_key)
        if cache.geocoded:
            # Already geocoded, skip
            return
    except CityGeoCache.DoesNotExist:
        pass
    
    # Geocode in background thread to not block the request
    thread = threading.Thread(target=geocode_async, args=(city_name, state_code))
    thread.daemon = True
    thread.start()
    
    logger.info(f"Triggered auto-geocoding for student city: {city_name}/{state_code}")


@receiver(post_save, sender=InstructorProfile)
def auto_geocode_instructor_city(sender, instance, created, **kwargs):
    """
    Automatically geocode city when an InstructorProfile is created or updated.
    """
    # Only process if has city
    if not instance.city:
        return
    
    city_name = instance.city.name
    state_code = instance.city.state.code
    
    # Check if already geocoded
    city_key = CityGeoCache.normalize_city_key(city_name, state_code)
    try:
        cache = CityGeoCache.objects.get(city_key=city_key)
        if cache.geocoded:
            # Already geocoded, skip
            return
    except CityGeoCache.DoesNotExist:
        pass
    
    # Geocode in background thread to not block the request
    thread = threading.Thread(target=geocode_async, args=(city_name, state_code))
    thread.daemon = True
    thread.start()
    
    logger.info(f"Triggered auto-geocoding for instructor city: {city_name}/{state_code}")
