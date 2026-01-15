#!/usr/bin/env python
"""
Listar todos os usuários do sistema
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

users = User.objects.all()

print(f'\n📋 USUÁRIOS NO SISTEMA ({users.count()}):')
print('=' * 80)

for user in users:
    print(f'\n👤 {user.username}')
    print(f'   Email: {user.email}')
    print(f'   Nome: {user.first_name} {user.last_name}')
    print(f'   Staff: {user.is_staff}')
    print(f'   Superuser: {user.is_superuser}')
    
    # Verificar se tem perfil de instrutor
    has_instructor = hasattr(user, 'instructor_profile')
    print(f'   É Instrutor: {has_instructor}')
    
    if has_instructor:
        prof = user.instructor_profile
        print(f'      → Visível: {prof.is_visible}')
        print(f'      → Verificado: {prof.is_verified}')
        print(f'      → Cidade: {prof.city.name if prof.city else "Não definida"}')
        print(f'      → Estado: {prof.city.state if prof.city else "Não definido"}')
        print(f'      → Lat/Long: {prof.latitude}/{prof.longitude}')
        
        # Verificar se aparece no mapa
        if prof.is_visible and prof.latitude and prof.longitude:
            print(f'      → ✅ APARECE NO MAPA')
        else:
            print(f'      → ⚠️  NÃO APARECE NO MAPA')
            if not prof.is_visible:
                print(f'         (perfil não visível)')
            if not prof.latitude or not prof.longitude:
                print(f'         (sem coordenadas)')

print('\n' + '=' * 80)
