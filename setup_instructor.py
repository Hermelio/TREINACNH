#!/usr/bin/env python
"""
Script para criar cidade e adicionar instrutor profile ao usuário de teste
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from marketplace.models import InstructorProfile, City, State

try:
    # Obter usuário
    user = User.objects.get(username='admin_test')
    print(f'✓ Usuário encontrado: {user.username}')
    
    # Obter ou criar cidade de São Paulo
    state_sp = State.objects.get(code='SP')
    city, created = City.objects.get_or_create(
        name='Sao Paulo',
        state=state_sp,
        defaults={'is_active': True}
    )
    
    if created:
        print(f'✓ Cidade criada: {city.name} - {city.state.code}')
    else:
        city.is_active = True
        city.save()
        print(f'✓ Cidade já existe: {city.name} - {city.state.code}')
    
    # Criar ou atualizar InstructorProfile
    from decimal import Decimal
    profile, created = InstructorProfile.objects.get_or_create(
        user=user,
        defaults={
            'city': city,
            'bio': 'Instrutor administrativo de teste com acesso completo',
            'gender': 'M',
            'age': 35,
            'years_experience': 10,
            'has_own_car': True,
            'car_model': 'Honda Civic 2020',
            'available_morning': True,
            'available_afternoon': True,
            'available_evening': True,
            'base_price_per_hour': Decimal('80.00'),
            'is_verified': True,
            'is_visible': True,
        }
    )
    
    if created:
        print(f'✓ InstructorProfile verificado criado')
    else:
        profile.is_verified = True
        profile.is_visible = True
        profile.city = city
        profile.save()
        print(f'✓ InstructorProfile atualizado para verificado')
    
    print('\n' + '='*60)
    print('SUCESSO! Usuário pronto para testes')
    print('='*60)
    print(f'URL Login: http://72.61.36.89:8080/contas/login/')
    print(f'Usuário: admin_test')
    print(f'Senha: Admin@2026')
    print('='*60)
    
except Exception as e:
    print(f'✗ Erro: {e}')
    import traceback
    traceback.print_exc()
