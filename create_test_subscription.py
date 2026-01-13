"""
Script para criar assinatura de teste para instrutor.
"""
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from billing.models import Plan, Subscription
from marketplace.models import InstructorProfile

# Buscar plano padrão
plan = Plan.objects.filter(is_active=True).first()

if not plan:
    print("❌ Nenhum plano ativo encontrado!")
    exit(1)

# Buscar primeiro instrutor
instructor = InstructorProfile.objects.first()

if not instructor:
    print("❌ Nenhum instrutor encontrado!")
    print("   Crie um perfil de instrutor primeiro no admin.")
    exit(1)

# Criar assinatura expirando em 3 dias
today = date.today()
end_date = today + timedelta(days=3)

subscription, created = Subscription.objects.get_or_create(
    instructor=instructor,
    plan=plan,
    defaults={
        'status': 'ACTIVE',
        'start_date': today,
        'end_date': end_date,
        'notes': 'Assinatura de teste criada automaticamente'
    }
)

if created:
    print(f"✅ Assinatura criada com sucesso!")
    print(f"   Instrutor: {instructor.user.get_full_name()}")
    print(f"   Plano: {plan.name}")
    print(f"   Válida até: {end_date.strftime('%d/%m/%Y')}")
    print(f"   Status: {subscription.get_status_display()}")
else:
    print(f"ℹ️ Assinatura já existe:")
    print(f"   Instrutor: {instructor.user.get_full_name()}")
    print(f"   Plano: {plan.name}")
    print(f"   Válida até: {subscription.end_date.strftime('%d/%m/%Y')}")

print(f"\n🔗 Login: {instructor.user.username}")
print(f"🔗 Ver assinatura: http://72.61.36.89:8080/planos/minha-assinatura/")
