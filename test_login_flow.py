#!/usr/bin/env python
"""
Simular login completo e ver onde dá erro
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/var/www/TREINACNH')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User

print('Testando fluxo de login...\n')

# Test with client
client = Client()

# Try to access login page
print('1. Acessando página de login...')
response = client.get('/contas/entrar/')
print(f'   Status: {response.status_code}')

# Try to login
print('\n2. Fazendo login com admin_test...')
response = client.post('/contas/entrar/', {
    'username': 'admin_test',
    'password': 'admin123'
})
print(f'   Status: {response.status_code}')
print(f'   Redirect: {response.get("Location", "N/A")}')

# Follow redirect
if response.status_code == 302:
    print('\n3. Seguindo redirect...')
    redirect_url = response.get('Location')
    try:
        response = client.get(redirect_url, follow=True)
        print(f'   Final Status: {response.status_code}')
        if response.status_code == 500:
            print('   ❌ ERRO 500!')
            # Try to get error from response
            print(f'   Content: {response.content[:500]}')
    except Exception as e:
        print(f'   ❌ Exception: {type(e).__name__}: {str(e)}')
        import traceback
        traceback.print_exc()
