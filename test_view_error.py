#!/usr/bin/env python
"""
Testar a view que está causando erro 500
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/var/www/TREINACNH')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from marketplace.views import cities_list_view

# Create a test request
factory = RequestFactory()
request = factory.get('/instrutores/')
request.user = User.objects.filter(username='admin_test').first()

print('Testing cities_list_view...')
try:
    response = cities_list_view(request)
    print(f'✅ Success! Status: {response.status_code}')
except Exception as e:
    print(f'❌ Error: {type(e).__name__}: {str(e)}')
    import traceback
    traceback.print_exc()
