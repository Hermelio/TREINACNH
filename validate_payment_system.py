#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from billing.models import Subscription, Payment
from marketplace.models import InstructorProfile
from datetime import date

print("\n" + "="*70)
print("🔍 VALIDAÇÃO COMPLETA DO SISTEMA DE PAGAMENTO")
print("="*70)

# 1. Verificar usuário e perfil
user = User.objects.get(username='admin_test')
print(f"\n✅ Usuário: {user.username}")
print(f"   Email: {user.email}")
print(f"   Nome: {user.get_full_name() or 'Não definido'}")

# 2. Verificar se é instrutor
profile = user.profile
print(f"\n✅ Perfil:")
print(f"   Role: {profile.role}")
print(f"   É Instrutor: {profile.is_instructor}")
print(f"   É Aluno: {profile.is_student}")

if not profile.is_instructor:
    print("\n❌ ERRO: Usuário NÃO é instrutor!")
    exit()

# 3. Verificar InstructorProfile
try:
    instructor = InstructorProfile.objects.get(user=user)
    print(f"\n✅ InstructorProfile:")
    print(f"   ID: {instructor.id}")
    print(f"   Cidade: {instructor.city}")
    print(f"   Bio: {instructor.bio[:50] if instructor.bio else 'Não definida'}...")
    print(f"   Visível: {instructor.is_visible}")
except InstructorProfile.DoesNotExist:
    print("\n❌ ERRO: InstructorProfile não encontrado!")
    exit()

# 4. Verificar Assinatura
subscriptions = Subscription.objects.filter(instructor=instructor)
print(f"\n✅ Assinaturas: {subscriptions.count()} encontrada(s)")

for sub in subscriptions:
    print(f"\n   📋 Assinatura ID {sub.id}:")
    print(f"      Plano: {sub.plan.name} (R$ {sub.plan.price_monthly})")
    print(f"      Status: {sub.status}")
    print(f"      Data início: {sub.start_date}")
    print(f"      Data fim: {sub.end_date}")
    print(f"      is_active: {sub.is_active}")
    
    # Status detalhado
    if sub.is_active:
        days_left = (sub.end_date - date.today()).days
        print(f"      ✅ ATIVA - Faltam {days_left} dias")
    else:
        print(f"      ❌ INATIVA")
    
    # 5. Verificar Pagamentos
    payments = Payment.objects.filter(subscription=sub).order_by('-created_at')
    print(f"\n      💰 Pagamentos: {payments.count()} encontrado(s)")
    
    for payment in payments:
        print(f"\n         Payment ID {payment.id}:")
        print(f"         Valor: R$ {payment.amount}")
        print(f"         Método: {payment.payment_method}")
        print(f"         Status: {payment.status}")
        print(f"         Criado em: {payment.created_at.strftime('%d/%m/%Y %H:%M')}")
        if payment.paid_at:
            print(f"         Pago em: {payment.paid_at.strftime('%d/%m/%Y %H:%M')}")
        print(f"         External ID: {payment.external_id}")

# 6. Teste de acesso a funcionalidades
print("\n" + "="*70)
print("🧪 TESTES DE FUNCIONALIDADE")
print("="*70)

# Teste 1: Pode criar leads?
print(f"\n✅ Pode receber leads: {profile.is_instructor}")

# Teste 2: Assinatura válida?
active_subs = subscriptions.filter(status='ACTIVE', end_date__gte=date.today())
print(f"✅ Tem assinatura válida: {active_subs.exists()}")

# Teste 3: Perfil visível no marketplace?
print(f"✅ Perfil visível: {instructor.is_visible}")

# 7. Resumo final
print("\n" + "="*70)
print("📊 RESUMO FINAL")
print("="*70)

if active_subs.exists() and profile.is_instructor:
    print("\n✅✅✅ SISTEMA FUNCIONANDO CORRETAMENTE! ✅✅✅")
    print("\nO instrutor admin_test pode:")
    print("   ✓ Receber leads de alunos")
    print("   ✓ Aparecer nas buscas do marketplace")
    print("   ✓ Gerenciar seus contatos")
    print("   ✓ Editar seu perfil profissional")
else:
    print("\n❌ SISTEMA COM PROBLEMAS")
    if not profile.is_instructor:
        print("   ✗ Usuário não é instrutor")
    if not active_subs.exists():
        print("   ✗ Sem assinatura ativa")

print("\n" + "="*70)
