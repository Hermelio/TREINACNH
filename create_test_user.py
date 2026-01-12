#!/usr/bin/env python
"""
Script para criar usuário administrativo de teste com perfil de instrutor verificado
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile
from marketplace.models import InstructorProfile, City, State

# Dados do usuário
username = 'admin_test'
email = 'admin@treinacnh.com'
password = 'Admin@2026'
first_name = 'Admin'
last_name = 'TreinaCNH'

# Criar ou obter usuário
user, created = User.objects.get_or_create(
    username=username,
    defaults={
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'is_staff': True,
        'is_superuser': True,
    }
)

if created:
    user.set_password(password)
    user.save()
    print(f'✓ Usuário {username} criado com sucesso!')
else:
    print(f'✓ Usuário {username} já existe')

# Criar ou obter Profile
profile, created = Profile.objects.get_or_create(
    user=user,
    defaults={
        'cpf': '12345678901',
        'phone': '11987654321',
        'birth_date': '1990-01-01',
        'email_verified': True,
        'is_blocked': False,
    }
)

if created:
    print(f'✓ Profile criado para {username}')
else:
    print(f'✓ Profile já existe para {username}')

# Obter São Paulo (SP) ou primeira cidade disponível
try:
    state_sp = State.objects.get(code='SP')
    city = City.objects.filter(state=state_sp, is_active=True).first()
    
    if not city:
        # Pegar qualquer cidade ativa
        city = City.objects.filter(is_active=True).first()
    
    if city:
        # Criar ou obter InstructorProfile
        instructor, created = InstructorProfile.objects.get_or_create(
            user=user,
            defaults={
                'city': city,
                'cnh_number': '12345678901',
                'cnh_category': 'AB',
                'years_experience': 5,
                'vehicle_type': 'Carro',
                'has_own_vehicle': True,
                'bio': 'Instrutor administrativo de teste com acesso completo',
                'hourly_rate': 80.00,
                'is_visible': True,
                'is_verified': True,  # VERIFICADO para acesso completo
            }
        )
        
        if created:
            print(f'✓ InstructorProfile verificado criado para {username}')
            print(f'  Cidade: {city.name} - {city.state.code}')
        else:
            # Atualizar para verificado se já existe
            instructor.is_verified = True
            instructor.is_visible = True
            instructor.save()
            print(f'✓ InstructorProfile atualizado para verificado')
    else:
        print('⚠ Nenhuma cidade disponível para criar InstructorProfile')
        
except State.DoesNotExist:
    print('⚠ Estado SP não encontrado')
except Exception as e:
    print(f'⚠ Erro ao criar InstructorProfile: {e}')

print('\n' + '='*60)
print('CREDENCIAIS DE ACESSO:')
print('='*60)
print(f'URL: http://72.61.36.89:8080/contas/login/')
print(f'Usuário: {username}')
print(f'Senha: {password}')
print('='*60)
print('\nEste usuário tem:')
print('✓ Acesso administrativo completo')
print('✓ Perfil de instrutor verificado')
print('✓ Permissão para ver dados completos dos alunos (WhatsApp)')
print('✓ Acesso ao painel admin: /admin/')
