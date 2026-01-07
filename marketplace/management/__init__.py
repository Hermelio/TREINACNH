"""
Management command to import all Brazilian cities from IBGE API.
Usage: python manage.py import_ibge_cities
"""
import requests
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from marketplace.models import State, City


class Command(BaseCommand):
    help = 'Import all Brazilian states and cities from IBGE API'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando importação de cidades do IBGE...'))
        
        try:
            # Import states first
            self.stdout.write('Buscando estados...')
            states_url = 'https://servicodados.ibge.gov.br/api/v1/localidades/estados'
            response = requests.get(states_url, timeout=30)
            response.raise_for_status()
            states_data = response.json()
            
            states_dict = {}
            for state_data in states_data:
                state, created = State.objects.get_or_create(
                    code=state_data['sigla'],
                    defaults={'name': state_data['nome']}
                )
                states_dict[state_data['id']] = state
                if created:
                    self.stdout.write(f'  ✓ Estado criado: {state.code} - {state.name}')
            
            self.stdout.write(self.style.SUCCESS(f'\n{len(states_dict)} estados processados.\n'))
            
            # Import cities
            self.stdout.write('Buscando municípios (isso pode levar alguns minutos)...')
            cities_url = 'https://servicodados.ibge.gov.br/api/v1/localidades/municipios'
            response = requests.get(cities_url, timeout=60)
            response.raise_for_status()
            cities_data = response.json()
            
            created_count = 0
            updated_count = 0
            
            for i, city_data in enumerate(cities_data, 1):
                state_id = city_data['microrregiao']['mesorregiao']['UF']['id']
                state = states_dict.get(state_id)
                
                if not state:
                    self.stdout.write(self.style.WARNING(f'Estado não encontrado para {city_data["nome"]}'))
                    continue
                
                city_name = city_data['nome']
                
                # Check if city exists
                city, created = City.objects.get_or_create(
                    state=state,
                    name=city_name,
                    defaults={
                        'slug': slugify(f"{city_name}-{state.code}"),
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                
                # Progress indicator
                if i % 500 == 0:
                    self.stdout.write(f'  Processando... {i}/{len(cities_data)} municípios')
            
            self.stdout.write(self.style.SUCCESS(f'\n✓ Importação concluída!'))
            self.stdout.write(self.style.SUCCESS(f'  • {created_count} municípios criados'))
            self.stdout.write(self.style.SUCCESS(f'  • {updated_count} municípios já existiam'))
            self.stdout.write(self.style.SUCCESS(f'  • Total: {City.objects.count()} municípios no banco'))
            
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Erro ao conectar com API do IBGE: {e}'))
            self.stdout.write(self.style.WARNING('Verifique sua conexão com a internet e tente novamente.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Erro durante importação: {e}'))
