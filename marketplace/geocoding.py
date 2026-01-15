"""
Utility functions for geocoding addresses.
Uses ViaCEP for Brazilian addresses and Nominatim (OpenStreetMap) for coordinates.
"""
import requests
import logging
from decimal import Decimal
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from time import sleep

logger = logging.getLogger(__name__)


def get_address_from_cep(cep):
    """
    Get address details from Brazilian CEP using ViaCEP API.
    Returns dict with street, neighborhood, city, state or None if not found.
    """
    # Clean CEP (remove dots and dashes)
    cep_clean = cep.replace('-', '').replace('.', '').strip()
    
    if len(cep_clean) != 8:
        logger.warning(f'CEP inválido: {cep}')
        return None
    
    try:
        url = f'https://viacep.com.br/ws/{cep_clean}/json/'
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # ViaCEP returns {'erro': True} for invalid CEPs
            if 'erro' in data:
                logger.warning(f'CEP não encontrado: {cep}')
                return None
            
            return {
                'street': data.get('logradouro', ''),
                'neighborhood': data.get('bairro', ''),
                'city': data.get('localidade', ''),
                'state': data.get('uf', ''),
                'cep': cep_clean
            }
        else:
            logger.error(f'Erro ao buscar CEP {cep}: HTTP {response.status_code}')
            return None
            
    except requests.RequestException as e:
        logger.error(f'Erro de conexão ao buscar CEP {cep}: {str(e)}')
        return None


def geocode_address(street, neighborhood, city, state, cep=None):
    """
    Get latitude and longitude from address using Nominatim (OpenStreetMap).
    Returns tuple (latitude, longitude) or (None, None) if not found.
    """
    try:
        # Build address string (more specific to less specific)
        address_parts = []
        
        if street:
            address_parts.append(street)
        if neighborhood:
            address_parts.append(neighborhood)
        if city:
            address_parts.append(city)
        if state:
            address_parts.append(state)
        address_parts.append('Brazil')
        
        address_string = ', '.join(address_parts)
        
        # Initialize geocoder with user agent
        geolocator = Nominatim(user_agent='treinacnh_app', timeout=10)
        
        # Try to geocode with full address
        logger.info(f'Tentando geocode: {address_string}')
        location = geolocator.geocode(address_string)
        
        if location:
            logger.info(f'Coordenadas encontradas: {location.latitude}, {location.longitude}')
            return Decimal(str(location.latitude)), Decimal(str(location.longitude))
        
        # If failed, try with less specific address (neighborhood + city + state)
        if neighborhood and city and state:
            simplified_address = f'{neighborhood}, {city}, {state}, Brazil'
            logger.info(f'Tentando geocode simplificado: {simplified_address}')
            sleep(1)  # Rate limiting
            location = geolocator.geocode(simplified_address)
            
            if location:
                logger.info(f'Coordenadas encontradas (simplificado): {location.latitude}, {location.longitude}')
                return Decimal(str(location.latitude)), Decimal(str(location.longitude))
        
        # Last resort: try just city + state
        if city and state:
            minimal_address = f'{city}, {state}, Brazil'
            logger.info(f'Tentando geocode mínimo: {minimal_address}')
            sleep(1)  # Rate limiting
            location = geolocator.geocode(minimal_address)
            
            if location:
                logger.info(f'Coordenadas encontradas (cidade): {location.latitude}, {location.longitude}')
                return Decimal(str(location.latitude)), Decimal(str(location.longitude))
        
        logger.warning(f'Não foi possível encontrar coordenadas para: {address_string}')
        return None, None
        
    except GeocoderTimedOut:
        logger.error('Timeout ao buscar coordenadas')
        return None, None
    except GeocoderServiceError as e:
        logger.error(f'Erro do serviço de geocoding: {str(e)}')
        return None, None
    except Exception as e:
        logger.error(f'Erro inesperado ao geocodificar: {str(e)}')
        return None, None


def geocode_instructor_profile(instructor_profile):
    """
    Update instructor profile with coordinates based on their address.
    Returns True if coordinates were updated, False otherwise.
    """
    # Check if we have enough information
    if not instructor_profile.city:
        logger.warning(f'Instrutor {instructor_profile.id} sem cidade definida')
        return False
    
    city_name = instructor_profile.city.name
    state_code = instructor_profile.city.state.code
    
    # Try to get coordinates
    lat, lon = geocode_address(
        street=instructor_profile.address_street,
        neighborhood=instructor_profile.address_neighborhood,
        city=city_name,
        state=state_code,
        cep=instructor_profile.address_zip
    )
    
    if lat and lon:
        instructor_profile.latitude = lat
        instructor_profile.longitude = lon
        instructor_profile.save(update_fields=['latitude', 'longitude'])
        logger.info(f'Coordenadas atualizadas para instrutor {instructor_profile.id}: {lat}, {lon}')
        return True
    
    logger.warning(f'Não foi possível obter coordenadas para instrutor {instructor_profile.id}')
    return False
