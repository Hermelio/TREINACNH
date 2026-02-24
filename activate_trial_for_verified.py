"""
Script para ativar o trial dos instrutores verificados que ainda não têm trial ativo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile

print("=" * 70)
print("ATIVAÇÃO DO TRIAL PARA INSTRUTORES VERIFICADOS")
print("=" * 70)
print()

# Busca instrutores verificados sem trial
instructors_without_trial = InstructorProfile.objects.filter(
    is_verified=True,
    trial_start_date__isnull=True
)

print(f"📊 Instrutores verificados sem trial: {instructors_without_trial.count()}")
print()

if not instructors_without_trial.exists():
    print("✅ Todos os instrutores verificados já têm trial ativo!")
    print()
else:
    print("Ativando trial de 14 dias para:")
    print("-" * 70)
    
    for instructor in instructors_without_trial:
        name = instructor.user.get_full_name()
        city = instructor.city.name if instructor.city else "Sem cidade"
        
        # Ativar trial
        instructor.activate_trial()
        
        print(f"✅ {name} ({city})")
        print(f"   Trial de {instructor.trial_start_date.strftime('%d/%m/%Y')} até {instructor.trial_end_date.strftime('%d/%m/%Y')}")
        print(f"   Status: is_trial_active={instructor.is_trial_active}")
        print()
    
    print("-" * 70)
    print(f"✅ Trial ativado para {instructors_without_trial.count()} instrutores!")
    print()

# Verifica status final
print("=" * 70)
print("STATUS FINAL:")
print("=" * 70)

all_verified = InstructorProfile.objects.filter(is_verified=True)
with_trial = all_verified.filter(trial_start_date__isnull=False)
can_receive = sum(1 for i in all_verified if i.can_receive_leads())

print(f"Instrutores verificados: {all_verified.count()}")
print(f"Com trial iniciado: {with_trial.count()}")
print(f"Podem receber leads: {can_receive}")
print()
print("✅ Concluído!")
print()
