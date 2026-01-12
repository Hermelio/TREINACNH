"""
Script to populate state coordinates with capital coordinates
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import State

# Coordinates of Brazilian state capitals
STATE_COORDINATES = {
    'AC': (-8.77, -70.55),  # Rio Branco
    'AL': (-9.66, -35.73),  # Maceió
    'AM': (-3.07, -60.01),  # Manaus
    'AP': (0.03, -51.07),   # Macapá
    'BA': (-12.97, -38.51), # Salvador
    'CE': (-3.71, -38.54),  # Fortaleza
    'DF': (-15.83, -47.86), # Brasília
    'ES': (-20.32, -40.34), # Vitória
    'GO': (-16.67, -49.25), # Goiânia
    'MA': (-2.55, -44.30),  # São Luís
    'MG': (-19.92, -43.94), # Belo Horizonte
    'MS': (-20.51, -54.54), # Campo Grande
    'MT': (-15.60, -56.10), # Cuiabá
    'PA': (-1.45, -48.48),  # Belém
    'PB': (-7.11, -34.86),  # João Pessoa
    'PE': (-8.05, -34.90),  # Recife
    'PI': (-5.09, -42.80),  # Teresina
    'PR': (-25.42, -49.27), # Curitiba
    'RJ': (-22.90, -43.17), # Rio de Janeiro
    'RN': (-5.79, -35.21),  # Natal
    'RO': (-8.76, -63.90),  # Porto Velho
    'RR': (2.82, -60.67),   # Boa Vista
    'RS': (-30.03, -51.23), # Porto Alegre
    'SC': (-27.59, -48.55), # Florianópolis
    'SE': (-10.90, -37.07), # Aracaju
    'SP': (-23.55, -46.64), # São Paulo
    'TO': (-10.18, -48.33), # Palmas
}

def populate_coordinates():
    """Add coordinates to all states"""
    updated = 0
    for state in State.objects.all():
        if state.code in STATE_COORDINATES:
            lat, lon = STATE_COORDINATES[state.code]
            state.latitude = lat
            state.longitude = lon
            state.save()
            print(f"✓ {state.code} - {state.name}: ({lat}, {lon})")
            updated += 1
        else:
            print(f"✗ {state.code} - {state.name}: Coordenadas não encontradas")
    
    print(f"\n{updated} estados atualizados com sucesso!")

if __name__ == '__main__':
    print("Populando coordenadas dos estados brasileiros...")
    print("=" * 60)
    populate_coordinates()
