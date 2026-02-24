import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile, CityGeoCache
from django.utils.text import slugify

all_inst = InstructorProfile.objects.filter(is_visible=True, is_verified=True)
print('Total verificados/visíveis:', all_inst.count())

city_cache = {c.city_key: c for c in CityGeoCache.objects.filter(geocoded=True)}

count_map = 0
sem_coords = []
for inst in all_inst:
    lat = inst.latitude
    lng = inst.longitude
    fonte = 'proprio'
    if (lat is None or lng is None) and inst.city_id:
        key = slugify(inst.city.name) + '|' + inst.city.state.code
        cached = city_cache.get(key)
        if cached and cached.latitude and cached.longitude:
            lat = cached.latitude
            lng = cached.longitude
            fonte = 'city_cache (key=%s)' % key
        else:
            fonte = 'SEM CACHE (key=%s)' % key
    if lat is not None and lng is not None:
        count_map += 1
        print('  OK [%s] %s | %s' % (fonte, inst.user.get_full_name(), inst.city.name if inst.city_id else 'sem cidade'))
    else:
        sem_coords.append(inst)
        print('  FALTA COORDS: %s | cidade_id=%s' % (inst.user.get_full_name(), inst.city_id))

print()
print('Total no mapa:', count_map)
print('Sem coords (fora do mapa):', len(sem_coords))
