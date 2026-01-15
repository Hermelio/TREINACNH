#!/usr/bin/env python
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from billing.models import Subscription, Payment
from marketplace.models import InstructorProfile
from django.utils import timezone

# Pegar admin_test
user = User.objects.get(username='admin_test')
instructor = InstructorProfile.objects.get(user=user)

# Pegar assinatura expirada
subscription = Subscription.objects.filter(instructor=instructor).first()

if not subscription:
    print("❌ Nenhuma assinatura encontrada")
    exit()

print(f"Assinatura encontrada: {subscription}")
print(f"Status antes: {subscription.status}")
print(f"Data fim antes: {subscription.end_date}")
print(f"is_active antes: {subscription.is_active}")

# Simular pagamento aprovado
payment = Payment.objects.create(
    subscription=subscription,
    amount=subscription.plan.price_monthly,
    payment_method='PIX',
    status='APPROVED',
    external_id=f'test_payment_{timezone.now().timestamp()}',
    paid_at=timezone.now(),
    payment_details={'simulated': True, 'test': 'pagamento_fake'}
)

# Ativar assinatura (simular o que o webhook faria)
if subscription.end_date and subscription.end_date >= date.today():
    # Se ainda não expirou, extende de hoje
    new_end_date = subscription.end_date + timedelta(days=30)
else:
    # Se já expirou, começa hoje
    new_end_date = date.today() + timedelta(days=30)

subscription.end_date = new_end_date
subscription.status = 'ACTIVE'
subscription.save()

print("\n" + "="*60)
print("✅ PAGAMENTO SIMULADO COM SUCESSO!")
print("="*60)
print(f"💰 Payment ID: {payment.id}")
print(f"💳 Valor: R$ {payment.amount}")
print(f"📅 Data fim nova: {subscription.end_date}")
print(f"✅ Status: {subscription.status}")
print(f"🔓 is_active: {subscription.is_active}")
print("="*60)
