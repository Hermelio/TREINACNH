#!/usr/bin/env python
"""
Testar redirect após login
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/var/www/TREINACNH')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

users = User.objects.all()

print(f'\n📋 VERIFICANDO {users.count()} USUÁRIOS:\n')

for user in users:
    print(f'👤 {user.username} ({user.first_name} {user.last_name})')
    
    # Check if has profile
    has_profile = hasattr(user, 'profile')
    print(f'   Tem Profile: {has_profile}')
    
    if has_profile:
        profile = user.profile
        print(f'   Role: {profile.role} ({profile.get_role_display()})')
        print(f'   is_instructor (property): {profile.is_instructor}')
        
        # Check if has InstructorProfile
        has_instructor_profile = hasattr(user, 'instructor_profile')
        print(f'   Tem InstructorProfile: {has_instructor_profile}')
        
        # Check inconsistency
        if profile.is_instructor and not has_instructor_profile:
            print(f'   ⚠️  INCONSISTÊNCIA: Role=INSTRUCTOR mas não tem InstructorProfile!')
        elif not profile.is_instructor and has_instructor_profile:
            print(f'   ⚠️  INCONSISTÊNCIA: Role≠INSTRUCTOR mas tem InstructorProfile!')
    
    print()
