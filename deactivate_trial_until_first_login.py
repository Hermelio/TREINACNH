"""
Script para desativar o trial dos instrutores verificados
(trial só deve começar quando eles resetarem a senha)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile

print("=" * 70)
print("DESATIVAÇÃO DO TRIAL DOS INSTRUTORES VERIFICADOS")
print("=" * 70)
print()

# Busca instrutores verificados com trial ativo
instructors_with_trial = InstructorProfile.objects.filter(
    is_verified=True,
    trial_start_date__isnull=False
)

print(f"📊 Instrutores verificados com trial: {instructors_with_trial.count()}")
print()

if not instructors_with_trial.exists():
    print("✅ Nenhum trial para desativar")
    print()
else:
    print("Desativando trial (trial começará no primeiro login):")
    print("-" * 70)
    
    for instructor in instructors_with_trial:
        name = instructor.user.get_full_name()
        city = instructor.city.name if instructor.city else "Sem cidade"
        
        # Desativar trial mas manter verificado
        instructor.trial_start_date = None
        instructor.trial_end_date = None
        instructor.is_trial_active = False
        instructor.save(update_fields=['trial_start_date', 'trial_end_date', 'is_trial_active'])
        
        print(f"✅ {name} ({city})")
        print(f"   Status: Verificado (trial começará no primeiro login)")
        print()
    
    print("-" * 70)
    print(f"✅ Trial desativado para {instructors_with_trial.count()} instrutores!")
    print()

# Verifica status final
print("=" * 70)
print("STATUS FINAL:")
print("=" * 70)

all_verified = InstructorProfile.objects.filter(is_verified=True)
with_trial = all_verified.filter(trial_start_date__isnull=False)
can_receive = sum(1 for i in all_verified if i.can_receive_leads())

print(f"Instrutores verificados: {all_verified.count()}")
print(f"Com trial ativo: {with_trial.count()}")
print(f"Podem receber leads: {can_receive}")
print()
print("ℹ️  O trial será ativado automaticamente no primeiro login após reset de senha")
print()
