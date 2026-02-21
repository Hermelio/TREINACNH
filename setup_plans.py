import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()
from billing.models import Plan

plans = [
    {
        'name': 'Plano Básico',
        'description': 'Ideal para instrutores que estão começando.',
        'price_monthly': 29.90,
        'features': 'Perfil visível no site\nContato via WhatsApp\nAparece na lista de instrutores\nRecebe avaliações de alunos',
        'is_active': True,
        'order': 1,
    },
    {
        'name': 'Plano Profissional',
        'description': 'Para instrutores que querem mais visibilidade e alunos.',
        'price_monthly': 49.90,
        'features': 'Perfil completo visível no site\nContato via WhatsApp\nAparece no mapa de instrutores\nRecebe avaliações de alunos\nDestaque na lista da cidade\nSuporte por email',
        'is_active': True,
        'order': 2,
    },
    {
        'name': 'Plano Premium',
        'description': 'Máxima visibilidade para instrutores de alto desempenho.',
        'price_monthly': 89.90,
        'features': 'Tudo do Plano Profissional\nDestaque premium no mapa\nAparece em primeiro nas buscas\nSelo de instrutor verificado\nEstatísticas de visualizações\nSuporte prioritário',
        'is_active': True,
        'order': 3,
    },
]

for data in plans:
    obj, created = Plan.objects.update_or_create(name=data['name'], defaults=data)
    action = 'Criado' if created else 'Atualizado'
    print(f"{action}: {obj.name} - R$ {obj.price_monthly}/mes")

# Desativar plano antigo 'Plano Instrutor' se existir com nome diferente
old = Plan.objects.exclude(name__in=[p['name'] for p in plans])
for p in old:
    print(f"Desativando plano antigo: {p.name}")
    p.is_active = False
    p.save()

print(f"\nTotal de planos ativos: {Plan.objects.filter(is_active=True).count()}")
