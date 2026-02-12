#!/usr/bin/env python
"""
Script to verify all instructors that were imported and are visible
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile

# Get all visible instructors that are not verified
not_verified = InstructorProfile.objects.filter(is_verified=False, is_visible=True)

print(f"Instrutores não verificados e visíveis: {not_verified.count()}")
print("\nVerificando todos os instrutores importados...")
print("=" * 80)

count = 0
for inst in not_verified:
    inst.is_verified = True
    inst.save()
    count += 1
    print(f"✓ {count}. {inst.user.get_full_name()} - {inst.city}")

print("\n" + "=" * 80)
print(f"✅ {count} instrutores foram verificados com sucesso!")

# Show summary
all_instructors = InstructorProfile.objects.all()
print(f"\nResumo:")
print(f"  Total de instrutores: {all_instructors.count()}")
print(f"  Verificados: {all_instructors.filter(is_verified=True).count()}")
print(f"  Não verificados: {all_instructors.filter(is_verified=False).count()}")
