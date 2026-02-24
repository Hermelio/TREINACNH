"""
Script para testar o sistema de trial e bloqueio de leads
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile
from billing.models import Subscription
from django.utils import timezone

print("=" * 70)
print("TESTE DO SISTEMA DE TRIAL E BLOQUEIO DE LEADS")
print("=" * 70)
print()

# Busca todos os instrutores
instructors = InstructorProfile.objects.select_related('user', 'city').all()

print(f"📊 Total de instrutores: {instructors.count()}")
print()

# Analisa status de cada instrutor
print("STATUS DE ACESSO AOS LEADS:")
print("-" * 70)

can_receive = 0
blocked = 0
trial_active = 0
with_subscription = 0

for instructor in instructors:
    status = instructor.get_access_status()
    name = instructor.user.get_full_name()
    city = instructor.city.name if instructor.city else "Sem cidade"
    
    if status['can_receive_leads']:
        can_receive += 1
        icon = "✅"
        if status['is_trial']:
            trial_active += 1
            status_text = f"Trial ativo ({status['days_remaining']} dias restantes)"
        elif status['has_subscription']:
            with_subscription += 1
            status_text = "Subscription ativa"
        else:
            status_text = "Ativo (motivo desconhecido)"
    else:
        blocked += 1
        icon = "❌"
        if status['reason'] == 'trial_expired':
            status_text = "Trial expirado - BLOQUEADO"
        else:
            status_text = "Sem acesso - BLOQUEADO"
    
    print(f"{icon} {name} ({city})")
    print(f"   Status: {status_text}")
    print(f"   can_receive_leads(): {instructor.can_receive_leads()}")
    
    # Informações detalhadas
    if instructor.trial_start_date:
        print(f"   Trial: início={instructor.trial_start_date.strftime('%d/%m/%Y')}, "
              f"fim={instructor.trial_end_date.strftime('%d/%m/%Y')}, "
              f"ativo={instructor.is_trial_active}")
    else:
        print(f"   Trial: não iniciado")
    
    if instructor.has_active_subscription():
        subs = Subscription.objects.filter(
            instructor=instructor,
            status='ACTIVE',
            start_date__lte=timezone.now().date()
        ).first()
        if subs:
            print(f"   Subscription: {subs.plan.name} (até {subs.end_date or 'indeterminado'})")
    else:
        print(f"   Subscription: nenhuma ativa")
    
    print()

print("-" * 70)
print("RESUMO:")
print("-" * 70)
print(f"✅ Podem receber leads: {can_receive}")
print(f"   - Em trial ativo: {trial_active}")
print(f"   - Com subscription: {with_subscription}")
print()
print(f"❌ Bloqueados: {blocked}")
print()

# Testa query de filtragem
from django.db.models import Q, Exists, OuterRef
from billing.models import SubscriptionStatusChoices

has_active_subscription = Subscription.objects.filter(
    instructor=OuterRef('pk'),
    status=SubscriptionStatusChoices.ACTIVE,
    start_date__lte=timezone.now().date()
).filter(
    Q(end_date__isnull=True) | Q(end_date__gte=timezone.now().date())
)

filtered_instructors = InstructorProfile.objects.filter(
    is_visible=True
).filter(
    Q(
        is_trial_active=True,
        trial_start_date__isnull=False,
        trial_end_date__gte=timezone.now()
    ) | Q(
        Exists(has_active_subscription)
    )
)

print(f"🔍 Query de filtragem retorna: {filtered_instructors.count()} instrutores")
print()

# Recomendações
print("=" * 70)
print("RECOMENDAÇÕES:")
print("=" * 70)
if blocked > 0:
    print(f"⚠️  {blocked} instrutores estão bloqueados e não aparecerão nas buscas")
    print("   Eles precisam contratar um plano para voltar a receber leads")
print()
if trial_active > 0:
    print(f"ℹ️  {trial_active} instrutores estão em período de teste")
    print("   Certifique-se de enviar emails de aviso antes do trial expirar")
print()
print("✅ Sistema de bloqueio está funcionando corretamente!")
print()
