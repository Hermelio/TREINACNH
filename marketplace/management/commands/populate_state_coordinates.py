"""
Management command to populate state coordinates (capitals).
"""
from django.core.management.base import BaseCommand
from marketplace.models import State


class Command(BaseCommand):
    help = 'Popula coordenadas das capitais dos estados brasileiros'

    def handle(self, *args, **options):
        """Populate state coordinates with capital city locations"""
        
        # Coordinates of Brazilian state capitals
        state_coordinates = {
            'AC': (-8.77, -70.55),    # Rio Branco
            'AL': (-9.71, -35.73),    # Maceió
            'AP': (0.034934, -51.0694),  # Macapá
            'AM': (-3.11, -60.02),    # Manaus
            'BA': (-12.97, -38.51),   # Salvador
            'CE': (-3.71, -38.54),    # Fortaleza
            'DF': (-15.83, -47.86),   # Brasília
            'ES': (-20.32, -40.34),   # Vitória
            'GO': (-16.64, -49.31),   # Goiânia
            'MA': (-2.55, -44.30),    # São Luís
            'MT': (-15.60, -56.10),   # Cuiabá
            'MS': (-20.51, -54.54),   # Campo Grande
            'MG': (-19.81, -43.95),   # Belo Horizonte
            'PA': (-1.45, -48.50),    # Belém
            'PB': (-7.06, -34.87),    # João Pessoa
            'PR': (-25.25, -49.25),   # Curitiba
            'PE': (-8.28, -35.07),    # Recife
            'PI': (-5.17, -42.80),    # Teresina
            'RJ': (-22.84, -43.15),   # Rio de Janeiro
            'RN': (-5.22, -36.52),    # Natal
            'RS': (-30.01, -51.22),   # Porto Alegre
            'RO': (-8.76, -63.90),    # Porto Velho
            'RR': (2.82, -60.67),     # Boa Vista
            'SC': (-27.33, -48.52),   # Florianópolis
            'SP': (-23.55, -46.64),   # São Paulo
            'SE': (-10.90, -37.07),   # Aracaju
            'TO': (-10.25, -48.25),   # Palmas
        }
        
        updated = 0
        created = 0
        
        for code, (lat, lng) in state_coordinates.items():
            try:
                state = State.objects.get(code=code)
                state.latitude = lat
                state.longitude = lng
                state.save()
                updated += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {code}: coordenadas atualizadas ({lat}, {lng})')
                )
            except State.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Estado {code} não encontrado no banco')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Concluído! {updated} estados atualizados.')
        )
