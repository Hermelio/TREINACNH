"""
Management command to import all Brazilian cities from IBGE API.
Usage: python manage.py import_ibge_cities
"""
import requests
from django.core.management.base import BaseCommand
from marketplace.models import State, City


class Command(BaseCommand):
    help = 'Import all Brazilian states and cities from IBGE API'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando importação de cidades do IBGE...'))

        try:
            # ── States ───────────────────────────────────────────────────
            self.stdout.write('Buscando estados...')
            states_url = 'https://servicodados.ibge.gov.br/api/v1/localidades/estados'
            response = requests.get(states_url, timeout=30)
            response.raise_for_status()
            states_data = response.json()

            states_dict = {}          # ibge_state_id -> State instance
            for state_data in sorted(states_data, key=lambda s: s['sigla']):
                state, created = State.objects.get_or_create(
                    code=state_data['sigla'],
                    defaults={'name': state_data['nome']}
                )
                states_dict[state_data['id']] = state
                if created:
                    self.stdout.write(f'  ✓ Estado criado: {state.code} - {state.name}')

            self.stdout.write(self.style.SUCCESS(f'\n{len(states_dict)} estados processados.\n'))

            # ── Cities ────────────────────────────────────────────────────
            self.stdout.write('Buscando municípios (isso pode levar alguns minutos)...')
            cities_url = 'https://servicodados.ibge.gov.br/api/v1/localidades/municipios'
            response = requests.get(cities_url, timeout=120)
            response.raise_for_status()
            cities_data = response.json()

            created_count = 0
            updated_count = 0
            error_count = 0

            for i, city_data in enumerate(cities_data, 1):
                try:
                    ibge_id = city_data['id']
                    state_ibge_id = city_data['microrregiao']['mesorregiao']['UF']['id']
                    state = states_dict.get(state_ibge_id)
                    if not state:
                        self.stdout.write(
                            self.style.WARNING(f'Estado IBGE {state_ibge_id} não encontrado para {city_data["nome"]}')
                        )
                        error_count += 1
                        continue

                    city_name = city_data['nome']

                    # 1) Try by ibge_id first (idempotent re-runs)
                    city = City.objects.filter(ibge_id=ibge_id).first()
                    if city:
                        # Ensure name/state are up-to-date
                        if city.name != city_name or city.state_id != state.pk:
                            city.name = city_name
                            city.state = state
                            city.save(update_fields=['name', 'state'])
                        updated_count += 1
                        continue

                    # 2) Try by state+name (cities that existed before ibge_id was added)
                    city = City.objects.filter(state=state, name=city_name).first()
                    if city:
                        city.ibge_id = ibge_id
                        city.is_active = True
                        city.save(update_fields=['ibge_id', 'is_active'])
                        updated_count += 1
                        continue

                    # 3) Create new city (slug generated + conflict-safe via City.save())
                    city = City(state=state, name=city_name, ibge_id=ibge_id, is_active=True)
                    city.save()
                    created_count += 1

                except Exception as e:
                    error_count += 1
                    if error_count <= 10:
                        self.stdout.write(self.style.WARNING(f'Erro ao processar município {i}: {e}'))

                # Progress indicator every 500 cities
                if i % 500 == 0:
                    self.stdout.write(f'  Processando... {i}/{len(cities_data)} municípios')

            self.stdout.write(self.style.SUCCESS('\n✓ Importação concluída!'))
            self.stdout.write(self.style.SUCCESS(f'  • {created_count} municípios criados'))
            self.stdout.write(self.style.SUCCESS(f'  • {updated_count} municípios já existiam / atualizados'))
            if error_count:
                self.stdout.write(self.style.WARNING(f'  • {error_count} erros'))
            self.stdout.write(self.style.SUCCESS(f'  • Total: {City.objects.count()} municípios no banco'))

        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Erro ao conectar com API do IBGE: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Erro durante importação: {e}'))
            raise
