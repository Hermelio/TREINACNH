#!/usr/bin/env python
"""
Atualizar endereço do admin_test e calcular coordenadas automaticamente
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/var/www/TREINACNH')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from marketplace.models import InstructorProfile
from marketplace.geocoding import geocode_instructor_profile

# Buscar admin_test
admin = User.objects.filter(username='admin_test').first()

if not admin:
    print('❌ Usuário admin_test não encontrado')
    sys.exit(1)

if not hasattr(admin, 'instructor_profile'):
    print('❌ admin_test não é instrutor')
    sys.exit(1)

prof = admin.instructor_profile

print(f'📋 ENDEREÇO ATUAL:')
print(f'   Rua: {prof.address_street or "Não definido"}')
print(f'   Bairro: {prof.address_neighborhood or "Não definido"}')
print(f'   CEP: {prof.address_zip or "Não definido"}')
print(f'   Latitude: {prof.latitude}')
print(f'   Longitude: {prof.longitude}')
print()

# Atualizar endereço
prof.address_street = 'Rua Francisca Queiros, 1000'
prof.address_neighborhood = 'Jardim São Luis'
prof.address_zip = '05875-270'
prof.save()

print(f'✅ ENDEREÇO ATUALIZADO')
print()

# Geocodificar automaticamente
print(f'🔍 Calculando coordenadas automaticamente...')
success = geocode_instructor_profile(prof)

# Recarregar para ver as coordenadas atualizadas
prof.refresh_from_db()

print()
print(f'📍 RESULTADO:')
print(f'   Rua: {prof.address_street}')
print(f'   Bairro: {prof.address_neighborhood}')
print(f'   CEP: {prof.address_zip}')
print(f'   Cidade: {prof.city.name}')
print(f'   Estado: {prof.city.state.code}')
print(f'   Latitude: {prof.latitude}')
print(f'   Longitude: {prof.longitude}')
print()

if success and prof.latitude and prof.longitude:
    print(f'✅ SUCESSO! Instrutor aparecerá no mapa com a localização exata!')
    print(f'   Google Maps: https://www.google.com/maps?q={prof.latitude},{prof.longitude}')
    print(f'   Marketplace: http://72.61.36.89:8080/marketplace/map/')
else:
    print(f'⚠️  Não foi possível calcular as coordenadas automaticamente')
    print(f'   Verifique o endereço e tente novamente')
