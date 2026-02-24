"""
Script para criar plano padrão para instrutores.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from billing.models import Plan

# Criar plano padrão
plan, created = Plan.objects.get_or_create(
    name='Plano Instrutor',
    defaults={
        'description': 'Plano mensal para instrutores autônomos',
        'price_monthly': 49.99,
        'features': '''Perfil completo visível no site
Contato via WhatsApp
Aparece no mapa de instrutores
Recebe avaliações de alunos
Suporte por email''',
        'is_active': True,
        'order': 1
    }
)

if created:
    print(f"✅ Plano criado com sucesso!")
    print(f"   Nome: {plan.name}")
    print(f"   Preço: R$ {plan.price_monthly}/mês")
    print(f"   ID: {plan.id}")
else:
    print(f"ℹ️ Plano já existe:")
    print(f"   Nome: {plan.name}")
    print(f"   Preço: R$ {plan.price_monthly}/mês")
    print(f"   ID: {plan.id}")

print(f"\n🔗 Acesse: http://72.61.36.89:8080/admin/billing/plan/")
