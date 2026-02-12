#!/usr/bin/env python
"""
Script to check instructor verification status
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile

instructors = InstructorProfile.objects.all()
print(f"Total: {instructors.count()} instrutores")
print(f"Verificados: {instructors.filter(is_verified=True).count()}")
print(f"Não verificados: {instructors.filter(is_verified=False).count()}")
print("\nPrimeiros 10:")
for i in instructors[:10]:
    print(f"ID {i.id}: {i.user.get_full_name()} - Verificado: {i.is_verified}")
