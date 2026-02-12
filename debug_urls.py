"""
Script para debugar URLs e ver qual view está sendo chamada
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import resolve
from django.test import RequestFactory

# Testar URL /instrutores/
factory = RequestFactory()
request = factory.get('/instrutores/')

try:
    match = resolve('/instrutores/')
    print(f"URL: /instrutores/")
    print(f"View function: {match.func}")
    print(f"View name: {match.url_name}")
    print(f"App name: {match.app_name}")
    print(f"Namespace: {match.namespace}")
    print(f"Kwargs: {match.kwargs}")
    
    # Verificar qual arquivo contém a view
    import inspect
    print(f"\nView module: {inspect.getmodule(match.func)}")
    print(f"View file: {inspect.getfile(match.func)}")
    
except Exception as e:
    print(f"Erro ao resolver URL: {e}")

# Verificar se views_map.py ainda existe
import os
views_map_path = os.path.join(os.path.dirname(__file__), 'marketplace', 'views_map.py')
print(f"\n\nArquivo views_map.py existe? {os.path.exists(views_map_path)}")

# Verificar se template instructors_map.html ainda existe
template_path = os.path.join(os.path.dirname(__file__), 'templates', 'marketplace', 'instructors_map.html')
print(f"Template instructors_map.html existe? {os.path.exists(template_path)}")

# Listar todos os templates em marketplace
template_dir = os.path.join(os.path.dirname(__file__), 'templates', 'marketplace')
if os.path.exists(template_dir):
    print(f"\nTemplates em marketplace/:")
    for f in os.listdir(template_dir):
        if f.endswith('.html'):
            print(f"  - {f}")
