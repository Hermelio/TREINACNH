# Seed all official CNH categories (get_or_create — safe to re-run).

from django.db import migrations

# (code, label, sort_order)
CNH_CATEGORIES = [
    ('ACC', 'Ciclomotores (até 50cc)',                        1),
    ('A',   'Motocicletas e similares',                         2),
    ('B',   'Automóveis',                                      3),
    ('C',   'Veículos de carga (caminhões)',                    4),
    ('D',   'Veículos de passageiros (ônibus / micro-ônibus)', 5),
    ('E',   'Combinados (carretas e veículos com reboque)',     6),
    ('AB',  'Moto + Carro (A e B)',                             7),
    ('AC',  'Moto + Caminhão (A e C)',                         8),
    ('AD',  'Moto + Ônibus (A e D)',                           9),
    ('AE',  'Moto + Carreta (A e E)',                          10),
]


def seed_categories(apps, schema_editor):
    CategoryCNH = apps.get_model('marketplace', 'CategoryCNH')
    for code, label, sort_order in CNH_CATEGORIES:
        obj, created = CategoryCNH.objects.get_or_create(
            code=code,
            defaults={'label': label, 'sort_order': sort_order},
        )
        if not created:
            # Update label and sort_order on existing rows so they stay current.
            updated = False
            if obj.label != label:
                obj.label = label
                updated = True
            if obj.sort_order != sort_order:
                obj.sort_order = sort_order
                updated = True
            if updated:
                obj.save(update_fields=['label', 'sort_order'])


def noop(apps, schema_editor):
    """Reverse is a no-op: keep existing rows to avoid data loss."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0013_expand_categorycnh_code'),
    ]

    operations = [
        migrations.RunPython(seed_categories, noop),
    ]
