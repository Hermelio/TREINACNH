import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory, TestCase
from django.contrib.auth import get_user_model
from accounts.models import Profile
from marketplace.models import InstructorProfile, StudentLead, City, State, CategoryCNH
from django.db.models import Q

User = get_user_model()

SEP = "=" * 60
OK  = "  OK "
ERR = "  ERRO"
WARN= "  AVISO"

errors = []

def ok(msg):   print(f"{OK}  {msg}")
def err(msg):  print(f"{ERR} {msg}"); errors.append(msg)
def warn(msg): print(f"{WARN} {msg}")
def section(title): print(f"\n{SEP}\n{title}\n{SEP}")

# ─────────────────────────────────────────────────────────────
section("1. MODELOS E PROPRIEDADES")
# ─────────────────────────────────────────────────────────────

# 1a. is_student_data_complete does NOT require cpf
import inspect
src = inspect.getsource(Profile.is_student_data_complete.fget)
if 'self.cpf' in src:
    err("is_student_data_complete ainda exige CPF!")
else:
    ok("is_student_data_complete NÃO exige CPF")

# 1b. StudentDataForm does NOT have cpf field
from accounts.forms import StudentDataForm
f = StudentDataForm()
if 'cpf' in f.fields:
    err("StudentDataForm ainda tem campo CPF!")
else:
    ok("StudentDataForm não tem campo CPF")

required_student_fields = ['first_name', 'last_name', 'email', 'whatsapp_number',
                            'cnh_categories', 'state', 'preferred_city']
for field in required_student_fields:
    if field not in f.fields:
        err(f"StudentDataForm falta campo obrigatório: {field}")
    else:
        ok(f"StudentDataForm tem campo: {field}")

# ─────────────────────────────────────────────────────────────
section("2. FLUXO DO ALUNO")
# ─────────────────────────────────────────────────────────────

# 2a. URL routes exist
from django.urls import reverse, NoReverseMatch
urls_to_check = [
    ('accounts:register',            []),
    ('accounts:login',               []),
    ('accounts:complete_student_data', []),
    ('accounts:complete_profile',    []),
    ('accounts:dashboard',           []),
    ('marketplace:cities_list',      []),
]
for name, args in urls_to_check:
    try:
        url = reverse(name, args=args)
        ok(f"URL existe: {name} → {url}")
    except NoReverseMatch:
        err(f"URL não encontrada: {name}")

# 2b. Registration creates StudentLead
from accounts.views import register_view
import inspect as insp
src_register = insp.getsource(register_view)
if 'StudentLead' in src_register:
    ok("register_view cria StudentLead para novos alunos")
else:
    err("register_view NÃO cria StudentLead")

# 2c. complete_student_data_view saves whatsapp, city, cnh_categories
from accounts.views import complete_student_data_view
src_complete = insp.getsource(complete_student_data_view)
for field in ['whatsapp_number', 'preferred_city', 'cnh_categories', 'is_profile_complete']:
    if field in src_complete:
        ok(f"complete_student_data_view salva: {field}")
    else:
        err(f"complete_student_data_view NÃO salva: {field}")

# 2d. lead_create_view guards incomplete students
from marketplace.views import lead_create_view
src_lead = insp.getsource(lead_create_view)
if 'is_student_data_complete' in src_lead:
    ok("lead_create_view bloqueia alunos sem perfil completo")
else:
    err("lead_create_view NÃO bloqueia alunos incompletos")

# 2e. instructor_detail_view sets student_data_incomplete flag
from marketplace.views import instructor_detail_view
src_detail = insp.getsource(instructor_detail_view)
if 'student_data_incomplete' in src_detail:
    ok("instructor_detail_view passa flag student_data_incomplete ao template")
else:
    err("instructor_detail_view NÃO passa flag student_data_incomplete")

# ─────────────────────────────────────────────────────────────
section("3. FLUXO DO INSTRUTOR")
# ─────────────────────────────────────────────────────────────

# 3a. instructor_profile_edit creates profile if not exists
from marketplace.views import instructor_profile_edit_view
src_edit = insp.getsource(instructor_profile_edit_view)
if 'InstructorProfile.DoesNotExist' in src_edit:
    ok("instructor_profile_edit_view trata perfil inexistente")
else:
    err("instructor_profile_edit_view não trata perfil inexistente")

# 3b. Instructor URL routes
instructor_urls = [
    ('marketplace:instructor_profile_edit', []),
    ('marketplace:cities_list',             []),
]
for name, args in instructor_urls:
    try:
        url = reverse(name, args=args)
        ok(f"URL existe: {name} → {url}")
    except NoReverseMatch:
        err(f"URL não encontrada: {name}")

# 3c. can_receive_leads exists on InstructorProfile
if hasattr(InstructorProfile, 'can_receive_leads'):
    ok("InstructorProfile.can_receive_leads() existe")
else:
    err("InstructorProfile.can_receive_leads() NÃO existe")

# 3d. Instructor registration creates InstructorProfile
src_register = insp.getsource(register_view)
if 'InstructorProfile' in src_register or 'instructor_profile' in src_register.lower():
    ok("register_view trata cadastro de instrutor")
else:
    warn("register_view pode não criar InstructorProfile automaticamente")

# ─────────────────────────────────────────────────────────────
section("4. DADOS REAIS NO BANCO")
# ─────────────────────────────────────────────────────────────

total_students = Profile.objects.filter(role='STUDENT').count()
complete_students = sum(1 for p in Profile.objects.filter(role='STUDENT') if p.is_student_data_complete)
ok(f"Alunos completos (podem contatar): {complete_students}/{total_students}")

total_instructors = InstructorProfile.objects.count()
visible = InstructorProfile.objects.filter(is_visible=True).count()
verified = InstructorProfile.objects.filter(is_verified=True).count()
can_recv = sum(1 for i in InstructorProfile.objects.all() if i.can_receive_leads())
ok(f"Instrutores total: {total_instructors} | visíveis: {visible} | verificados: {verified} | recebendo leads: {can_recv}")

# Students with profile but NOT complete — what's missing
students_incomplete = [p for p in Profile.objects.filter(role='STUDENT').select_related('user') if not p.is_student_data_complete]
if students_incomplete:
    warn(f"{len(students_incomplete)} alunos ainda incompletos (precisam preencher o formulário)")
else:
    ok("Todos os alunos cadastrados têm perfil completo")

# ─────────────────────────────────────────────────────────────
section("5. MIDDLEWARE / ACESSO")
# ─────────────────────────────────────────────────────────────

from core.middleware import ProfileCompletionMiddleware
exempt = ProfileCompletionMiddleware.EXEMPT_PREFIXES
for path in ['/admin/', '/contas/completar-cadastro/', '/contas/sair/']:
    if any(path.startswith(e) for e in exempt):
        ok(f"Middleware isenta: {path}")
    else:
        err(f"Middleware NÃO isenta: {path}")

# complete_student_data must also be exempt
if '/contas/completar-dados-aluno/' in exempt:
    ok("Middleware isenta: /contas/completar-dados-aluno/")
else:
    err("Middleware NÃO isenta /contas/completar-dados-aluno/ — loop infinito possível!")

# ─────────────────────────────────────────────────────────────
section("RESUMO")
# ─────────────────────────────────────────────────────────────
if errors:
    print(f"\n❌ {len(errors)} problema(s) encontrado(s):")
    for e in errors:
        print(f"   • {e}")
else:
    print("\n✅ Todos os checks passaram. Fluxos de aluno e instrutor OK.")
