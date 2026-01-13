#!/usr/bin/env python
"""
Criar usuário aluno de teste: hermelio
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/var/www/TREINACNH')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()

# Dados do usuário
username = 'hermelio'
email = 'hermelio@treinacnh.com.br'
password = 'teste123'
first_name = 'Hermelio'
last_name = 'Silva'

# Verificar se usuário já existe
if User.objects.filter(username=username).exists():
    print(f'⚠️  Usuário {username} já existe. Atualizando senha...')
    user = User.objects.get(username=username)
    user.set_password(password)
    user.save()
    print(f'✅ Senha atualizada para: {password}')
else:
    # Criar usuário
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    print(f'✅ Usuário criado: {username}')

# Garantir que o perfil existe e NÃO é instrutor
profile, created = Profile.objects.get_or_create(user=user)
# is_instructor é uma property que verifica se existe InstructorProfile
# Não precisa setar, o usuário é aluno por padrão (sem InstructorProfile)
profile.email_verified = True
profile.save()

if created:
    print(f'✅ Perfil de aluno criado')
else:
    print(f'✅ Perfil atualizado')

# Verificar se realmente NÃO é instrutor
has_instructor_profile = hasattr(user, 'instructor_profile')
print(f'   É instrutor? {has_instructor_profile}')
print(f'   É aluno? {not has_instructor_profile}')

print(f'\n📋 CREDENCIAIS DE ACESSO:')
print(f'   URL: http://72.61.36.89:8080/accounts/login/')
print(f'   Username: {username}')
print(f'   Password: {password}')
print(f'\n✅ Pronto para testar como ALUNO!')
