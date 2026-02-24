import os, django, uuid
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import Profile
from marketplace.models import StudentLead

def gen_ext_id():
    return 'web_' + uuid.uuid4().hex[:20]

students_complete = [p for p in Profile.objects.filter(role='STUDENT').select_related('user', 'preferred_city') if p.is_student_data_complete]

created_count = 0
updated_count = 0
skipped_count = 0

for profile in students_complete:
    user = profile.user
    city = profile.preferred_city
    if not city:
        skipped_count += 1
        continue

    lead, created = StudentLead.objects.get_or_create(
        email=user.email,
        defaults={
            'external_id': gen_ext_id(),
            'name': user.get_full_name() or user.username,
            'phone': profile.whatsapp_number or profile.phone or '',
            'city': city,
            'state': city.state,
            'accept_whatsapp': profile.accept_whatsapp_messages,
            'accept_terms': profile.accept_terms,
            'accept_email': True,
        }
    )
    if created:
        lead.categories.set(profile.cnh_categories.all())
        created_count += 1
        print(f"  CRIADO  {user.get_full_name()} <{user.email}> — {city}")
    else:
        # Update in case data changed
        lead.name  = user.get_full_name() or user.username
        lead.phone = profile.whatsapp_number or profile.phone or ''
        lead.city  = city
        lead.state = city.state
        lead.save(update_fields=['name', 'phone', 'city', 'state'])
        lead.categories.set(profile.cnh_categories.all())
        updated_count += 1
        print(f"  UPDATED {user.get_full_name()} <{user.email}> — {city}")

print(f"\nTotal alunos completos: {len(students_complete)}")
print(f"  Leads criados:    {created_count}")
print(f"  Leads atualizados:{updated_count}")
print(f"  Sem cidade (skip):{skipped_count}")
