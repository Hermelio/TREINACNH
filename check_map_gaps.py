import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile, CityGeoCache
from django.utils.text import slugify

insts = InstructorProfile.objects.filter(is_visible=True, is_verified=True).select_related('user', 'city', 'city__state')
total = insts.count()
with_own = insts.filter(latitude__isnull=False, longitude__isnull=False).count()
without = insts.filter(latitude__isnull=True).count()

print(f"Verificados e visíveis: {total}")
print(f"Com lat/lng próprio  (aparecem no mapa): {with_own}")
print(f"Sem lat/lng próprio  (somem do mapa)   : {without}")
print()

can_fix = 0
cannot_fix = 0

for inst in insts.filter(latitude__isnull=True):
    ckey = slugify(inst.city.name) + '|' + inst.city.state.code
    try:
        gc = CityGeoCache.objects.get(city_key=ckey, geocoded=True)
        has_city = bool(gc.latitude and gc.longitude)
        city_lat = gc.latitude
        city_lon = gc.longitude
    except CityGeoCache.DoesNotExist:
        has_city = False
        city_lat = city_lon = None

    tag = "✅ pode usar cidade" if has_city else "❌ sem coords em lugar algum"
    print(f"  {tag} | {inst.user.get_full_name()} | {inst.city.name}/{inst.city.state.code}")
    if has_city:
        print(f"         city cache: {city_lat}, {city_lon}")
        can_fix += 1
    else:
        cannot_fix += 1

print()
print(f"Pueden ser corrigidos via city cache : {can_fix}")
print(f"Sem solução automática (sem geocache): {cannot_fix}")
