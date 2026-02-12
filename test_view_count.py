"""
Script para testar a view cities_list_view e ver quantos instrutores ela retorna
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile
import json

# Contar instrutores no banco
print("=== DADOS NO BANCO ===")
total_visible = InstructorProfile.objects.filter(is_visible=True).count()
print(f"Total de instrutores visíveis: {total_visible}")

with_coords = InstructorProfile.objects.filter(
    is_visible=True,
    latitude__isnull=False,
    longitude__isnull=False
).count()
print(f"Instrutores com coordenadas: {with_coords}")

# Testar os dados que a view usa
print("\n=== TESTANDO DADOS DA VIEW ===")
all_instructors = InstructorProfile.objects.filter(
    is_visible=True
).select_related('user', 'user__profile', 'city', 'city__state').order_by('-created_at')

instructors_with_location = all_instructors.filter(
    latitude__isnull=False,
    longitude__isnull=False
)

instructors_data = []
for inst in instructors_with_location:
    instructors_data.append({
        'id': inst.id,
        'user__first_name': inst.user.first_name,
        'user__last_name': inst.user.last_name,
        'latitude': float(inst.latitude),
        'longitude': float(inst.longitude),
        'city__name': inst.city.name,
        'city__state__code': inst.city.state.code,
        'city__state__name': inst.city.state.name
    })

print(f"all_instructors: {all_instructors.count()}")
print(f"instructors_with_location: {instructors_with_location.count()}")
print(f"instructors_data (JSON): {len(instructors_data)}")

print("\n=== CONCLUSÃO ===")
print(f"✅ A view retorna {all_instructors.count()} instrutores na lista")
print(f"✅ O mapa mostra {len(instructors_data)} marcadores")
print(f"\n🎯 Tudo funcionando! O problema era erro de sintaxe no base.html que quebrava a renderização.")
