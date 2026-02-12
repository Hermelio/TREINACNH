"""
Create missing cities for instructor leads
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import City, State

# Cities to add
missing_cities = [
    ('Bonfim', 'RR'),
    ('Horizontina', 'RS'),
]

created = 0
for city_name, state_code in missing_cities:
    try:
        state = State.objects.get(code=state_code)
        city, created_now = City.objects.get_or_create(
            name=city_name,
            state=state,
            defaults={'is_active': True}
        )
        if created_now:
            print(f"✓ Created: {city_name}/{state_code}")
            created += 1
        else:
            print(f"→ Already exists: {city_name}/{state_code}")
    except State.DoesNotExist:
        print(f"❌ State not found: {state_code}")

print(f"\nTotal created: {created}")
