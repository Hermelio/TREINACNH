#!/usr/bin/env python
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from billing.models import Subscription
from marketplace.models import InstructorProfile

# Pegar admin_test
user = User.objects.get(username='admin_test')
instructor = InstructorProfile.objects.get(user=user)

# Verificar se já tem assinatura
subscription = Subscription.objects.filter(instructor=instructor).first()

if subscription:
    print(f"Assinatura encontrada: {subscription}")
    print(f"Status atual: {subscription.status}")
    print(f"Data fim antes: {subscription.end_date}")
    
    # Expirar a assinatura (colocar data de fim para ontem)
    subscription.end_date = date.today() - timedelta(days=1)
    subscription.status = 'expired'
    subscription.save()
    
    print(f"\n✅ Assinatura expirada!")
    print(f"Data fim agora: {subscription.end_date}")
    print(f"Status agora: {subscription.status}")
    print(f"is_active: {subscription.is_active}")
else:
    print("❌ Nenhuma assinatura encontrada para admin_test")
    print("Você precisa criar uma assinatura primeiro indo em /planos/")
