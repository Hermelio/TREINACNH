"""
Management command to import student leads from CSV file.
Usage: python manage.py import_student_leads
"""
import csv
import json
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from marketplace.models import State, StudentLead


class Command(BaseCommand):
    help = 'Import student leads from StudentLead.csv file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='StudentLead.csv',
            help='Path to CSV file (default: StudentLead.csv in project root)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without actually saving data'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))
        
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                created_count = 0
                updated_count = 0
                error_count = 0
                skipped_count = 0
                
                # Ensure all states exist first
                self._ensure_states_exist()
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is line 1)
                    try:
                        result = self._process_row(row, dry_run)
                        
                        if result == 'created':
                            created_count += 1
                        elif result == 'updated':
                            updated_count += 1
                        elif result == 'skipped':
                            skipped_count += 1
                            
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(f'Error on line {row_num}: {str(e)}')
                        )
                        self.stdout.write(self.style.ERROR(f'Row data: {row}'))
                
                # Summary
                self.stdout.write('\n' + '='*60)
                self.stdout.write(self.style.SUCCESS(f'Import completed!'))
                self.stdout.write(f'Created: {created_count}')
                self.stdout.write(f'Updated: {updated_count}')
                self.stdout.write(f'Skipped: {skipped_count}')
                if error_count > 0:
                    self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))
                self.stdout.write('='*60)
                
        except FileNotFoundError:
            raise CommandError(f'File not found: {file_path}')
        except Exception as e:
            raise CommandError(f'Error reading file: {str(e)}')

    def _ensure_states_exist(self):
        """Ensure all Brazilian states exist in database"""
        states_data = [
            ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'),
            ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'),
            ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'),
            ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
            ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
            ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'),
            ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'),
            ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
        ]
        
        for code, name in states_data:
            State.objects.get_or_create(code=code, defaults={'name': name})

    def _process_row(self, row, dry_run):
        """Process a single CSV row with correct relations and notification suppression"""
        from marketplace.models import City, CategoryCNH, StudentLead
        external_id = row.get('id', '').strip()
        name = row.get('name', '').strip()
        phone = row.get('phone', '').strip()
        city_name = row.get('city', '').strip()
        state_code = row.get('state', '').strip().upper()
        category_str = row.get('category', '').strip().upper()

        # Parse metadata JSON
        metadata_str = row.get('metadata', '{}')
        try:
            metadata = json.loads(metadata_str) if metadata_str else {}
        except json.JSONDecodeError:
            metadata = {}

        # Extract email from metadata
        email = metadata.get('email', '').strip()

        # Parse boolean fields
        has_theory = metadata.get('hasTheory', False)
        accept_email = row.get('acceptMarketing', '').lower() == 'true'
        accept_whatsapp = row.get('acceptWhatsApp', '').lower() == 'true'
        accept_terms = row.get('acceptTerms', '').lower() == 'true'
        is_contacted = row.get('isContacted', '').lower() == 'true'

        # Parse dates
        contacted_at = None
        contacted_at_str = row.get('contactedAt', '').strip()
        if contacted_at_str:
            try:
                contacted_at = datetime.fromisoformat(contacted_at_str.replace('Z', '+00:00'))
            except ValueError:
                pass

        notes = row.get('notes', '').strip()

        # Validation
        if not external_id:
            self.stdout.write(self.style.WARNING(f'Skipping row without ID'))
            return 'skipped'

        if not name or not phone or not state_code:
            self.stdout.write(self.style.WARNING(f'Skipping incomplete row: {external_id}'))
            return 'skipped'

        # Get or skip if state doesn't exist
        try:
            state = State.objects.get(code=state_code)
        except State.DoesNotExist:
            self.stdout.write(self.style.WARNING(f'Unknown state code: {state_code}'))
            return 'skipped'

        # Resolve city foreign key
        city = None
        if city_name:
            city_qs = City.objects.filter(name__iexact=city_name, state=state)
            city = city_qs.first()
            if not city:
                self.stdout.write(self.style.WARNING(f'City not found: {city_name}/{state_code}'))

        # Resolve categories (ManyToMany)
        categories = []
        if category_str:
            for cat_code in category_str:
                cat = CategoryCNH.objects.filter(code=cat_code).first()
                if cat:
                    categories.append(cat)
                else:
                    self.stdout.write(self.style.WARNING(f'Category not found: {cat_code}'))

        if dry_run:
            self.stdout.write(f'Would import: {name} - {city_name}/{state_code} - Cat. {category_str}')
            return 'created'

        # Create or update lead (do not send notifications)
        lead, created = StudentLead.objects.update_or_create(
            external_id=external_id,
            defaults={
                'name': name,
                'phone': phone,
                'email': email,
                'city': city,
                'state': state,
                'has_theory': has_theory,
                'accept_email': accept_email,
                'accept_whatsapp': accept_whatsapp,
                'accept_terms': accept_terms,
                'is_contacted': is_contacted,
                'contacted_at': contacted_at,
                'metadata': metadata,
                'notes': notes,
                'notified_about_instructor': False,
            }
        )
        if categories:
            lead.categories.set(categories)
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {name} - {city_name}/{state_code}'))
            return 'created'
        else:
            self.stdout.write(f'→ Updated: {name} - {city_name}/{state_code}')
            return 'updated'
