"""
Script para verificar o role do usuário de teste
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import Profile
from django.contrib.auth.models import User

print("=== VERIFICANDO USUÁRIOS ===\n")

# Listar todos os usuários não-staff
users = User.objects.filter(is_staff=False, is_superuser=False)[:10]

for user in users:
    if hasattr(user, 'profile'):
        print(f"Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.profile.role}")
        print(f"  Is instructor: {user.profile.is_instructor}")
        print()
