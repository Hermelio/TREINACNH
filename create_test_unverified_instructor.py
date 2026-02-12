#!/usr/bin/env python
"""
Script to create a test unverified instructor
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile
from marketplace.models import InstructorProfile, City, State

# Create test user
try:
    user = User.objects.create_user(
        username='instrutor_teste_nao_verificado',
        email='teste@naoverificado.com',
        password='teste123',
        first_name='Instrutor',
        last_name='Teste Não Verificado'
    )
    print(f"✓ Usuário criado: {user.username}")
    
    # Update profile
    profile = user.profile
    profile.role = 'INSTRUCTOR'
    profile.cpf = '12345678901'
    profile.whatsapp_number = '+5511999999999'
    profile.save()
    print(f"✓ Profile atualizado: {profile.role}")
    
    # Get a city
    city = City.objects.first()
    
    # Create instructor profile (NOT VERIFIED)
    instructor = InstructorProfile.objects.create(
        user=user,
        city=city,
        bio='Instrutor de teste aguardando verificação de documentos.',
        years_experience=5,
        has_own_car=True,
        is_verified=False,  # NOT VERIFIED
        is_visible=True
    )
    print(f"✓ Instrutor criado: ID {instructor.id}")
    print(f"  Nome: {instructor.user.get_full_name()}")
    print(f"  Cidade: {instructor.city}")
    print(f"  Verificado: {instructor.is_verified}")
    print(f"  Visível: {instructor.is_visible}")
    
    print(f"\n✅ Instrutor de teste criado com sucesso!")
    print(f"Acesse: http://72.61.36.89:8080/instrutores/instrutor/{instructor.id}/")
    
except Exception as e:
    print(f"❌ Erro: {e}")
