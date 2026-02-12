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

from django.test import RequestFactory
from marketplace.views import cities_list_view
from marketplace.models import InstructorProfile

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

# Testar a view
print("\n=== TESTANDO A VIEW ===")
factory = RequestFactory()
request = factory.get('/instrutores/cidades/')

response = cities_list_view(request)
print(f"Status code: {response.status_code}")

# Verificar contexto
if hasattr(response, 'context_data'):
    context = response.context_data
    if 'all_instructors' in context:
        count = context['all_instructors'].count()
        print(f"all_instructors no contexto: {count}")
    if 'instructors_json' in context:
        import json
        instructors_json = json.loads(context['instructors_json'])
        print(f"instructors_json tem {len(instructors_json)} instrutores")

print("\n=== CONCLUSÃO ===")
print(f"A view deveria retornar {total_visible} instrutores")
print(f"O mapa deveria mostrar {with_coords} marcadores")
