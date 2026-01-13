#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import RoleChoices

# Fix admin_test role
user = User.objects.get(username='admin_test')
print(f"Antes: role={user.profile.role}, is_instructor={user.profile.is_instructor}")

# Set correct enum value (UPPERCASE)
user.profile.role = RoleChoices.INSTRUCTOR  # 'INSTRUCTOR' not 'instructor'
user.profile.save()

# Reload from DB to confirm
user.refresh_from_db()
print(f"Depois: role={user.profile.role}, is_instructor={user.profile.is_instructor}")

if user.profile.is_instructor:
    print("✅ admin_test agora é instrutor!")
else:
    print("❌ Ainda não funcionou")
