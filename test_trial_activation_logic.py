"""
Teste da lógica de ativação de trial:
- Novos instrutores: trial ativado automaticamente na aprovação de documentos
- Instrutores antigos (9 verificados): trial ativado apenas no primeiro login
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile

print("=" * 70)
print("TESTE DA LÓGICA DE ATIVAÇÃO DE TRIAL")
print("=" * 70)
print()

# Verificar os 9 instrutores antigos (verificados, sem trial)
verified_no_trial = InstructorProfile.objects.filter(
    is_verified=True,
    trial_start_date__isnull=True
).select_related('user')

print(f"📊 Instrutores verificados SEM trial (antigos): {verified_no_trial.count()}")
print("   → Trial será ativado no PRIMEIRO LOGIN")
print()

for instructor in verified_no_trial:
    print(f"   • {instructor.user.get_full_name()} ({instructor.city})")
    print(f"     Status: is_verified={instructor.is_verified}, trial_start_date={instructor.trial_start_date}")

print()
print("-" * 70)
print()

# Verificar instrutores com trial ativo
with_trial = InstructorProfile.objects.filter(
    is_verified=True,
    trial_start_date__isnull=False
).select_related('user')

print(f"📊 Instrutores verificados COM trial (novos): {with_trial.count()}")
print("   → Trial foi ativado na APROVAÇÃO DE DOCUMENTOS")
print()

for instructor in with_trial:
    print(f"   • {instructor.user.get_full_name()} ({instructor.city})")
    print(f"     Trial iniciado em: {instructor.trial_start_date}")
    print(f"     Expira em: {instructor.trial_end_date}")
    print(f"     Pode receber leads: {instructor.can_receive_leads()}")

print()
print("=" * 70)
print("COMPORTAMENTO ESPERADO:")
print("=" * 70)
print()
print("✅ Novos instrutores:")
print("   1. Documentos aprovados → is_verified=True")
print("   2. Como era is_verified=False antes → activate_trial() é chamado")
print("   3. Trial começa imediatamente")
print()
print("✅ Instrutores antigos (9):")
print("   1. Documentos aprovados → is_verified=True")
print("   2. Como era is_verified=True antes → activate_trial() NÃO é chamado")
print("   3. Trial só será ativado no primeiro login (via signal)")
print()
