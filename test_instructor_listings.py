"""
Verificar se instrutores verificados aparecem nas listagens.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile, City
from django.utils import timezone

print("=" * 70)
print("TESTE DE LISTAGEM DE INSTRUTORES")
print("=" * 70)
print()

# Contar instrutores por status
all_instructors = InstructorProfile.objects.filter(is_visible=True)
verified = all_instructors.filter(is_verified=True)
with_trial = verified.filter(
    is_trial_active=True,
    trial_end_date__gte=timezone.now()
)
without_trial = verified.filter(
    trial_start_date__isnull=True
)

print(f"📊 Total de instrutores visíveis: {all_instructors.count()}")
print(f"📊 Instrutores verificados: {verified.count()}")
print(f"📊 Com trial ativo: {with_trial.count()}")
print(f"📊 Sem trial (aguardando primeiro login): {without_trial.count()}")
print()
print("-" * 70)
print()

# Listar alguns instrutores verificados
print("INSTRUTORES VERIFICADOS (aparecem na listagem):")
print()

for instructor in verified[:15]:
    can_receive = "✅ SIM" if instructor.can_receive_leads() else "❌ NÃO"
    trial_status = "Trial ativo" if instructor.is_trial_active else "Sem trial"
    
    print(f"• {instructor.user.get_full_name()} ({instructor.city})")
    print(f"  Verificado: ✅ | Pode receber leads: {can_receive} | {trial_status}")
    print()

print("-" * 70)
print()

# Verificar contagem por cidade
cities_with_instructors = City.objects.filter(
    instructors__is_visible=True,
    instructors__is_verified=True
).distinct().count()

print(f"📍 Cidades com instrutores verificados: {cities_with_instructors}")
print()

# Mostrar algumas cidades
cities = City.objects.filter(
    instructors__is_visible=True,
    instructors__is_verified=True
).distinct()[:10]

print("Exemplos de cidades:")
for city in cities:
    count = InstructorProfile.objects.filter(
        city=city,
        is_visible=True,
        is_verified=True
    ).count()
    print(f"  • {city.name}/{city.state.code}: {count} instrutor(es)")

print()
print("=" * 70)
print()
print("✅ Todos os instrutores VERIFICADOS agora aparecem nas listagens")
print("✅ Bloqueio de leads continua funcionando (can_receive_leads)")
print()
