import os, sys, django
sys.path.insert(0, '/var/www/TREINACNH')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from django.contrib.auth.models import User
from marketplace.models import InstructorProfile
from accounts.models import Profile

# Ultimos 5 usuarios registrados
print('=== ULTIMOS 5 USUARIOS CADASTRADOS ===')
for u in User.objects.order_by('-date_joined')[:5]:
    p = Profile.objects.filter(user=u).first()
    ip = InstructorProfile.objects.filter(user=u).first()
    role = p.role if p else 'SEM PROFILE'
    print(f'  {u.date_joined.strftime("%d/%m/%Y %H:%M")} | {u.get_full_name() or u.username} | role={role} | has_instructor_profile={bool(ip)}')

# Instrutores (role=INSTRUCTOR) sem InstructorProfile
print('\n=== INSTRUTORES sem InstructorProfile (erro grave) ===')
instructor_users = Profile.objects.filter(role='INSTRUCTOR')
missing_ip = []
for p in instructor_users:
    if not InstructorProfile.objects.filter(user=p.user).exists():
        missing_ip.append(p)
print(f'  Total com role=INSTRUCTOR: {instructor_users.count()}')
print(f'  Sem InstructorProfile: {len(missing_ip)}')
for p in missing_ip[:10]:
    print(f'  -> {p.user.get_full_name()} | {p.user.email} | joined={p.user.date_joined.strftime("%d/%m/%Y")}')

# InstructorProfiles pendentes de verificacao
print('\n=== InstructorProfiles PENDENTES DE VERIFICACAO ===')
pending = InstructorProfile.objects.filter(is_verified=False).order_by('-created_at')
print(f'  Total pendentes: {pending.count()}')
for ip in pending[:5]:
    print(f'  -> {ip.user.get_full_name()} | {ip.user.email} | created={ip.created_at.strftime("%d/%m/%Y")}')

# Alunos
print('\n=== ALUNOS (role=STUDENT) ===')
students = Profile.objects.filter(role='STUDENT')
print(f'  Total: {students.count()}')
for p in students.order_by('-user__date_joined')[:5]:
    print(f'  -> {p.user.get_full_name() or p.user.username} | {p.user.email} | joined={p.user.date_joined.strftime("%d/%m/%Y")}')

# Usuarios sem Profile
print('\n=== USUARIOS SEM PROFILE (erro grave) ===')
no_profile = []
for u in User.objects.filter(is_staff=False, is_superuser=False):
    if not Profile.objects.filter(user=u).exists():
        no_profile.append(u)
print(f'  Total: {len(no_profile)}')
for u in no_profile[:5]:
    print(f'  -> {u.get_full_name() or u.username} | {u.email}')

print('\nDiagnostico concluido.')
