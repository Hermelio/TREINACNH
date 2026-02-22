#!/usr/bin/env python
"""Remove assinaturas de teste"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from billing.models import Subscription
from django.contrib.auth.models import User

# Encontrar usuário
user = User.objects.filter(email='admin@teste.com').first()

if not user:
    print('❌ Usuário admin@teste.com não encontrado')
    exit(1)

# Buscar assinaturas
subs = Subscription.objects.filter(user=user)
print(f'\n📋 Assinaturas encontradas: {subs.count()}')

for s in subs:
    print(f'\nID: {s.id}')
    print(f'Plano: {s.plan.name}')
    print(f'Status: {s.status}')
    print(f'Ativa: {s.is_active}')
    print(f'Início: {s.start_date}')
    print(f'Fim: {s.end_date}')
    
# Remover todas
count = subs.count()
subs.delete()
print(f'\n✅ {count} assinatura(s) removida(s)!')
print('✅ Você pode fazer um novo pagamento agora.')
