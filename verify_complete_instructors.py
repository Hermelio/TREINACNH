#!/usr/bin/env python
"""
Script to verify instructors that have complete profiles
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile

# Get instructors that are not verified but have complete data
instructors = InstructorProfile.objects.filter(is_verified=False)

print(f"Encontrados {instructors.count()} instrutores não verificados")
print("\nInstrutores com perfis completos (que podem ser verificados):")
print("=" * 80)

complete_profiles = []
for inst in instructors:
    # Check if profile is complete
    has_bio = bool(inst.bio and len(inst.bio) > 20)
    has_experience = inst.years_experience > 0
    has_categories = inst.categories.exists()
    has_location = bool(inst.latitude and inst.longitude)
    
    completeness_score = sum([has_bio, has_experience, has_categories, has_location])
    
    if completeness_score >= 2:  # At least 2 criteria met
        complete_profiles.append(inst)
        print(f"\nID {inst.id}: {inst.user.get_full_name()}")
        print(f"  Cidade: {inst.city}")
        print(f"  Bio: {'✓' if has_bio else '✗'} ({len(inst.bio) if inst.bio else 0} chars)")
        print(f"  Experiência: {'✓' if has_experience else '✗'} ({inst.years_experience} anos)")
        print(f"  Categorias: {'✓' if has_categories else '✗'} ({inst.categories.count()})")
        print(f"  Localização: {'✓' if has_location else '✗'}")
        print(f"  Score: {completeness_score}/4")

print(f"\n\nTotal de perfis completos: {len(complete_profiles)}")
print("\nDeseja verificar TODOS estes instrutores? (s/n): ", end='')

response = input().strip().lower()
if response == 's':
    count = 0
    for inst in complete_profiles:
        inst.is_verified = True
        inst.save()
        count += 1
        print(f"✓ Verificado: {inst.user.get_full_name()}")
    
    print(f"\n✅ {count} instrutores foram verificados com sucesso!")
else:
    print("\nOperação cancelada.")
