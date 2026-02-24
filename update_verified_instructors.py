"""
Script para atualizar o status de verificação dos instrutores.
Marca apenas os instrutores que foram realmente verificados pela equipe,
os demais ficam como "em análise".
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile, RoleChoices
from marketplace.models import InstructorProfile

# Dados dos instrutores que foram REALMENTE VERIFICADOS pela equipe
# (extraídos do arquivo InstructorLead ativos.csv)
# BUSCA POR TELEFONE pois este campo é único
VERIFIED_INSTRUCTORS = [
    {'name': 'Anderson Guimarães', 'phone': '3199955771', 'city': 'Belo Horizonte'},
    {'name': 'Juliano Rosa de Oliveira', 'phone': '14997966346', 'city': 'Itaí'},
    {'name': 'Alessandro Tiago de Barros', 'phone': '19989418604', 'city': 'Paulínia'},
    {'name': 'Diogo Ricardo Sampietri', 'phone': '19991021332', 'city': 'Paulínia'},
    {'name': 'merilyn kelly de moraes zanini', 'phone': '19998791858', 'city': 'Limeira'},
    {'name': 'Cleo Roberto Elibio Roldão', 'phone': '51996979850', 'city': 'Parobé'},
    {'name': 'Edimar de Souza', 'phone': '19983524053', 'city': 'Paulínia'},
    {'name': 'Paulo Kazuhiro Handa', 'phone': '11976281450', 'city': 'São Paulo'},
    {'name': 'Humberto Carloa Rosinholo', 'phone': '11941213043', 'city': 'São Bernardo do Campo'},
]

print("=" * 70)
print("ATUALIZAÇÃO DE STATUS DE VERIFICAÇÃO DOS INSTRUTORES")
print("=" * 70)
print()

# Busca todos os instrutores (users com profile role=INSTRUCTOR e que tem instructor_profile)
instructor_profiles = InstructorProfile.objects.select_related('user', 'user__profile', 'city').all()
total_instructors = instructor_profiles.count()

print(f"📊 Total de instrutores cadastrados: {total_instructors}")
print()

# Separa os que estão verificados atualmente
currently_verified = instructor_profiles.filter(is_verified=True)
print(f"✅ Atualmente verificados: {currently_verified.count()}")

# Lista os instrutores atualmente verificados
if currently_verified.exists():
    print("\nInstrutores atualmente marcados como verificados:")
    for instructor in currently_verified:
        phone = instructor.user.profile.phone if hasattr(instructor.user, 'profile') else ''
        verified_phones = [v['phone'] for v in VERIFIED_INSTRUCTORS]
        verified_mark = "✓" if phone in verified_phones else "✗"
        city_name = instructor.city.name if instructor.city else 'Sem cidade'
        state = instructor.city.state if instructor.city else ''
        print(f"  {verified_mark} {instructor.user.get_full_name()} - {city_name}/{state} - Tel: {phone}")

print()
print("-" * 70)
print("APLICANDO ALTERAÇÕES...")
print("-" * 70)
print()

# 1. DESMARCAR TODOS os instrutores como não verificados
print("1️⃣ Removendo verificação de TODOS os instrutores...")
unverified_count = instructor_profiles.update(is_verified=False)
print(f"   ✓ {unverified_count} instrutores desmarcados como verificados")
print()

# 2. MARCAR apenas os instrutores da lista como verificados
print("2️⃣ Marcando apenas os instrutores VERIFICADOS PELA EQUIPE...")
verified_count = 0
not_found = []

for instructor_data in VERIFIED_INSTRUCTORS:
    phone = instructor_data['phone']
    name = instructor_data['name']
    city_name = instructor_data['city']
    
    try:
        # Busca pelo telefone no Profile
        profile = Profile.objects.get(phone__endswith=phone)
        instructor_profile = InstructorProfile.objects.select_related('user', 'city').get(user=profile.user)
        
        instructor_profile.is_verified = True
        instructor_profile.save(update_fields=['is_verified'])
        verified_count += 1
        
        actual_city = instructor_profile.city.name if instructor_profile.city else 'Sem cidade'
        actual_state = instructor_profile.city.state if instructor_profile.city else ''
        print(f"   ✓ {instructor_profile.user.get_full_name()} ({actual_city}/{actual_state}) - Tel: {phone}")
        
    except Profile.DoesNotExist:
        not_found.append({'name': name, 'phone': phone, 'reason': 'Profile não encontrado'})
        print(f"   ⚠️  Não encontrado: {name} - Tel: {phone}")
    except InstructorProfile.DoesNotExist:
        not_found.append({'name': name, 'phone': phone, 'reason': 'InstructorProfile não encontrado'})
        print(f"   ⚠️  Sem perfil de instrutor: {name} - Tel: {phone}")
    except Profile.MultipleObjectsReturned:
        not_found.append({'name': name, 'phone': phone, 'reason': 'Múltiplos perfis encontrados'})
        print(f"   ⚠️  Múltiplos perfis: {name} - Tel: {phone}")

print()
print("-" * 70)
print("RESULTADO FINAL")
print("-" * 70)
print()
print(f"✅ Instrutores VERIFICADOS: {verified_count}/{len(VERIFIED_INSTRUCTORS)}")
print(f"⏳ Instrutores EM ANÁLISE: {total_instructors - verified_count}")
print()

if not_found:
    print("⚠️  Instrutores não encontrados no banco de dados:")
    for item in not_found:
        print(f"   - {item['name']} (Tel: {item['phone']}) - {item['reason']}")
    print()

# Verifica o status final
print("📋 Status final dos instrutores:")
verified_final = InstructorProfile.objects.filter(is_verified=True)
print(f"   Verificados: {verified_final.count()}")

unverified_final = InstructorProfile.objects.filter(is_verified=False)
print(f"   Em análise: {unverified_final.count()}")
print()

print("=" * 70)
print("✅ ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!")
print("=" * 70)
print()
print("ℹ️  Agora apenas os instrutores verificados pela equipe aparecerão como ativos.")
print("   Os demais precisarão passar pelo processo de verificação.")
print()
