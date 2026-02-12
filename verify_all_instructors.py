#!/usr/bin/env python
"""
Script to check instructor details and optionally verify them
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile

# Get all instructors
all_instructors = InstructorProfile.objects.all().order_by('-id')

print(f"Total de instrutores: {all_instructors.count()}")
print(f"Verificados: {all_instructors.filter(is_verified=True).count()}")
print(f"Não verificados: {all_instructors.filter(is_verified=False).count()}")

print("\n" + "=" * 100)
print("DETALHES DE TODOS OS INSTRUTORES:")
print("=" * 100)

for inst in all_instructors:
    status = "✓ VERIFICADO" if inst.is_verified else "✗ NÃO VERIFICADO"
    print(f"\nID {inst.id}: {inst.user.get_full_name()} - {status}")
    print(f"  Cidade: {inst.city}")
    print(f"  Email: {inst.user.email}")
    print(f"  Bio: {inst.bio[:50] if inst.bio else 'Sem bio'}...")
    print(f"  Experiência: {inst.years_experience} anos")
    print(f"  Categorias: {inst.categories.count()}")
    print(f"  Localização: {'Sim' if inst.latitude and inst.longitude else 'Não'}")
    print(f"  Visível: {inst.is_visible}")
    print(f"  Criado em: {inst.created_at.strftime('%d/%m/%Y')}")

print("\n" + "=" * 100)
print("Deseja verificar TODOS os instrutores não verificados? (s/n): ", end='')

response = input().strip().lower()
if response == 's':
    not_verified = InstructorProfile.objects.filter(is_verified=False)
    count = 0
    for inst in not_verified:
        inst.is_verified = True
        inst.save()
        count += 1
        print(f"✓ Verificado: {inst.user.get_full_name()}")
    
    print(f"\n✅ {count} instrutores foram verificados com sucesso!")
else:
    print("\nOperação cancelada.")
