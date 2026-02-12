"""
Script para verificar quantos instrutores têm coordenadas
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile

# Contar instrutores
total = InstructorProfile.objects.filter(is_visible=True).count()
with_coords = InstructorProfile.objects.filter(is_visible=True, latitude__isnull=False, longitude__isnull=False).count()
without_coords = total - with_coords

print(f"Total de instrutores visíveis: {total}")
print(f"Com coordenadas (lat/lng): {with_coords}")
print(f"Sem coordenadas: {without_coords}")

# Listar instrutores sem coordenadas
print("\nInstrutores SEM coordenadas:")
instructors_no_coords = InstructorProfile.objects.filter(
    is_visible=True,
    latitude__isnull=True
).select_related('user', 'city', 'city__state')

for inst in instructors_no_coords:
    print(f"  - {inst.user.get_full_name()} | Cidade: {inst.city.name}, {inst.city.state.code}")
    if inst.city.latitude and inst.city.longitude:
        print(f"    ⚠️  Cidade TEM coordenadas: {inst.city.latitude}, {inst.city.longitude}")
    else:
        print(f"    ❌ Cidade também NÃO tem coordenadas")
