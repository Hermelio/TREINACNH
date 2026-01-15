#!/usr/bin/env python
"""
Verificar se o usuário admin tem perfil de instrutor
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

# Buscar admin
admin = User.objects.filter(username='admin').first()

if not admin:
    print('❌ Usuário admin não encontrado')
    sys.exit(1)

print(f'✅ Usuário admin encontrado')
print(f'   Username: {admin.username}')
print(f'   Email: {admin.email}')
print(f'   Nome: {admin.first_name} {admin.last_name}')
print(f'   Is staff: {admin.is_staff}')
print(f'   Is superuser: {admin.is_superuser}')
print()

# Verificar se tem perfil de instrutor
has_instructor = hasattr(admin, 'instructor_profile')
print(f'   Tem InstructorProfile: {has_instructor}')

if has_instructor and admin.instructor_profile:
    prof = admin.instructor_profile
    print(f'\n📋 DADOS DO INSTRUTOR:')
    print(f'   Ativo: {prof.is_active}')
    print(f'   Especialidades: {", ".join([s.name for s in prof.specialties.all()])}')
    print(f'   Cidade: {prof.city}')
    print(f'   Estado: {prof.state}')
    print(f'   Latitude: {prof.latitude}')
    print(f'   Longitude: {prof.longitude}')
    print(f'   Bio: {prof.bio[:50] if prof.bio else "Não definida"}...')
    
    # Verificar se apareceria no mapa
    if prof.is_active and prof.latitude and prof.longitude:
        print(f'\n✅ DEVE APARECER NO MAPA (ativo e com coordenadas)')
    else:
        print(f'\n⚠️  NÃO APARECE NO MAPA:')
        if not prof.is_active:
            print(f'   - Perfil não está ativo')
        if not prof.latitude or not prof.longitude:
            print(f'   - Sem coordenadas definidas')
else:
    print(f'\n❌ Admin NÃO é instrutor (não tem InstructorProfile)')
    print(f'   Para torná-lo instrutor, execute: setup_instructor.py')
