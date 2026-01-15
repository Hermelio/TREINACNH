#!/usr/bin/env python
"""
Adicionar coordenadas ao instrutor admin_test
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

# Buscar admin_test
admin = User.objects.filter(username='admin_test').first()

if not admin:
    print('❌ Usuário admin_test não encontrado')
    sys.exit(1)

if not hasattr(admin, 'instructor_profile'):
    print('❌ admin_test não é instrutor')
    sys.exit(1)

prof = admin.instructor_profile

print(f'📋 ANTES DA ATUALIZAÇÃO:')
print(f'   Cidade: {prof.city.name if prof.city else "Não definida"}')
print(f'   Latitude: {prof.latitude}')
print(f'   Longitude: {prof.longitude}')
print()

# Coordenadas do centro de São Paulo
# Praça da Sé - marco zero da cidade
prof.latitude = -23.5505
prof.longitude = -46.6333
prof.save()

print(f'✅ COORDENADAS ATUALIZADAS:')
print(f'   Cidade: {prof.city.name}')
print(f'   Latitude: {prof.latitude}')
print(f'   Longitude: {prof.longitude}')
print()

# Verificar se agora aparece no mapa
if prof.is_visible and prof.latitude and prof.longitude:
    print(f'✅ INSTRUTOR AGORA APARECE NO MAPA!')
    print(f'   Acesse: http://72.61.36.89:8080/marketplace/map/')
else:
    print(f'⚠️  Ainda não aparece no mapa')
    if not prof.is_visible:
        print(f'   - Perfil não visível')
