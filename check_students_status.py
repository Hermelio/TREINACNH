import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import Profile
from django.db.models import Q

students = Profile.objects.filter(role='STUDENT').select_related('user', 'preferred_city')
total = students.count()
complete = sum(1 for p in students if p.is_student_data_complete)
incomplete = total - complete

print(f'Total alunos: {total}')
print(f'Perfil completo (podem contatar): {complete}')
print(f'Perfil incompleto (ainda bloqueados): {incomplete}')

missing_wpp  = sum(1 for p in students if not p.whatsapp_number and not p.phone)
missing_city = sum(1 for p in students if not p.preferred_city_id)
missing_name = sum(1 for p in students if not p.user.first_name or not p.user.last_name)
missing_cats = sum(1 for p in students if not p.cnh_categories.exists())

print(f'  Sem WhatsApp/telefone: {missing_wpp}')
print(f'  Sem cidade: {missing_city}')
print(f'  Sem nome/sobrenome: {missing_name}')
print(f'  Sem categorias CNH: {missing_cats}')
