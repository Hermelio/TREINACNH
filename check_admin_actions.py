import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import inspect
from django.contrib import admin as django_admin
from marketplace import admin as mkt_admin
from marketplace.models import InstructorProfile, Lead, StudentLead, Appointment, City, CityGeoCache

OK   = "  OK "
ERR  = "  ERRO"
WARN = "  AVISO"
errors = []

def ok(msg):   print(f"{OK}  {msg}")
def err(msg):  print(f"{ERR} {msg}"); errors.append(msg)
def warn(msg): print(f"{WARN} {msg}")

SEP = "=" * 60

# -------------------------------------------------------------------
print(f"\n{SEP}\n1. SINTAXE E IMPORTS\n{SEP}")

# Check admin module imported correctly
try:
    from marketplace.admin import (
        InstructorProfileAdmin, LeadAdmin, StudentLeadAdmin,
        AppointmentAdmin, CityAdmin, CityGeoCacheAdmin
    )
    ok("Todas as classes Admin importadas com sucesso")
except ImportError as e:
    err(f"Import falhou: {e}")

# Check no ACTION_CHECKBOX_NAME usage
src = inspect.getsource(mkt_admin)
if 'ACTION_CHECKBOX_NAME' in src:
    err("admin.ACTION_CHECKBOX_NAME ainda presente no código!")
else:
    ok("Nenhum uso de ACTION_CHECKBOX_NAME")

# -------------------------------------------------------------------
print(f"\n{SEP}\n2. AÇÕES DO InstructorProfileAdmin\n{SEP}")

admin_site = django_admin.site
inst_admin = admin_site._registry.get(InstructorProfile)
if not inst_admin:
    err("InstructorProfile não registrado no admin site")
else:
    ok("InstructorProfile registrado no admin site")
    expected_actions = [
        'approve_instructors', 'make_unverified', 'make_visible',
        'make_invisible', 'export_to_csv',
        'trial_add_7', 'trial_add_14', 'trial_add_30',
        'trial_sub_7', 'trial_sub_14', 'trial_custom_days',
    ]
    for action in expected_actions:
        if hasattr(inst_admin, action):
            ok(f"  Ação existe: {action}")
        else:
            err(f"  Ação FALTA: {action}")

    # Check _adjust_trial internals
    src_adjust = inspect.getsource(inst_admin._adjust_trial)
    if 'update_fields' in src_adjust:
        ok("  _adjust_trial usa update_fields corretamente")
    else:
        warn("  _adjust_trial não usa update_fields")

    # Check trial_custom_days CSRF
    src_custom = inspect.getsource(inst_admin.trial_custom_days)
    if 'CSRF_COOKIE' in src_custom:
        warn("  trial_custom_days usa CSRF_COOKIE (pode ser vazio) — preferível get_token(request)")
    if "'_selected_action'" in src_custom:
        ok("  trial_custom_days usa '_selected_action' corretamente")
    if 'ACTION_CHECKBOX_NAME' in src_custom:
        err("  trial_custom_days ainda usa ACTION_CHECKBOX_NAME!")

# -------------------------------------------------------------------
print(f"\n{SEP}\n3. AÇÕES DO LeadAdmin\n{SEP}")

lead_admin = admin_site._registry.get(Lead)
if lead_admin:
    for action in ['mark_as_contacted', 'mark_as_closed', 'mark_as_spam']:
        if hasattr(lead_admin, action):
            ok(f"  Ação existe: {action}")
        else:
            err(f"  Ação FALTA: {action}")
else:
    err("Lead não registrado no admin site")

# -------------------------------------------------------------------
print(f"\n{SEP}\n4. AÇÕES DO StudentLeadAdmin\n{SEP}")

sl_admin = admin_site._registry.get(StudentLead)
if sl_admin:
    for action in ['notify_about_instructors', 'mark_as_contacted', 'export_phones']:
        if hasattr(sl_admin, action):
            ok(f"  Ação existe: {action}")
        else:
            err(f"  Ação FALTA: {action}")
    # Check export_phones safety when 0 phones
    src_phones = inspect.getsource(sl_admin.export_phones)
    if 'if lead.phone' in src_phones:
        ok("  export_phones filtra leads sem telefone")
    else:
        warn("  export_phones pode falhar com leads sem telefone")
else:
    err("StudentLead não registrado no admin site")

# -------------------------------------------------------------------
print(f"\n{SEP}\n5. AÇÕES DO AppointmentAdmin\n{SEP}")

appt_admin = admin_site._registry.get(Appointment)
if appt_admin:
    for action in ['confirm_appointments', 'complete_appointments', 'cancel_appointments']:
        if hasattr(appt_admin, action):
            ok(f"  Ação existe: {action}")
        else:
            err(f"  Ação FALTA: {action}")
else:
    err("Appointment não registrado no admin site")

# -------------------------------------------------------------------
print(f"\n{SEP}\n6. AÇÕES DO CityAdmin / CityGeoCacheAdmin\n{SEP}")

city_admin = admin_site._registry.get(__import__('marketplace.models', fromlist=['City']).City)
geo_admin  = admin_site._registry.get(CityGeoCache)

if city_admin and hasattr(city_admin, 'geocode_selected_cities'):
    ok("  CityAdmin: geocode_selected_cities existe")
else:
    err("  CityAdmin: geocode_selected_cities FALTA")

if geo_admin and hasattr(geo_admin, 'retry_failed_geocoding'):
    ok("  CityGeoCacheAdmin: retry_failed_geocoding existe")
else:
    err("  CityGeoCacheAdmin: retry_failed_geocoding FALTA")

# -------------------------------------------------------------------
print(f"\n{SEP}\n7. VERIFICAÇÃO DE manage.py check\n{SEP}")
import subprocess, sys
result = subprocess.run(
    ['python', 'manage.py', 'check', '--deploy', '--fail-level', 'ERROR'],
    capture_output=True, text=True
)
if result.returncode == 0:
    ok("manage.py check --deploy: sem erros críticos")
else:
    lines = (result.stdout + result.stderr).strip().split('\n')
    for l in lines[-10:]:
        if l.strip():
            warn(f"  {l}")

# -------------------------------------------------------------------
print(f"\n{SEP}\nRESUMO\n{SEP}")
if errors:
    print(f"\n❌ {len(errors)} problema(s):")
    for e in errors:
        print(f"   • {e}")
else:
    print("\n✅ Todas as ações verificadas — sem erros.")
