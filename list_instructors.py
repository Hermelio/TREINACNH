import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile
from django.contrib.auth import get_user_model

# Buscar instrutores
instructors = InstructorProfile.objects.all()[:5]
print(f"Total instrutores: {InstructorProfile.objects.count()}")
print("\nInstrutores:")
for ip in instructors:
    print(f"  - Username: {ip.user.username}")
    print(f"    Nome: {ip.user.get_full_name()}")
    print(f"    É instrutor: {ip.user.profile.is_instructor}")
    print()
