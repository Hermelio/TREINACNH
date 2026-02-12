"""
Management command to import instructor leads from CSV file.
Usage: python manage.py import_instructor_leads --file InstructorLead.csv
"""
import csv
import json
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.contrib.auth.models import User
from marketplace.models import State, City, CategoryCNH, InstructorProfile
from accounts.models import Profile


class Command(BaseCommand):
    help = 'Import instructor leads from InstructorLead.csv file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='InstructorLead.csv',
            help='Path to CSV file (default: InstructorLead.csv in project root)'
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
                
                for row_num, row in enumerate(reader, start=2):
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

    def _process_row(self, row, dry_run):
        """Process a single CSV row"""
        external_id = row.get('id', '').strip()
        name = row.get('name', '').strip()
        phone = row.get('phone', '').strip()
        city_name = row.get('city', '').strip()
        state_code = row.get('state', '').strip().upper()
        cpf = row.get('cpf', '').strip()
        cnh_categories = row.get('cnhCategories', '').strip()

        # Parse metadata JSON
        metadata_str = row.get('metadata', '{}')
        try:
            metadata = json.loads(metadata_str) if metadata_str else {}
        except json.JSONDecodeError:
            metadata = {}

        # Extract email from metadata
        email = metadata.get('email', '').strip()

        # Parse boolean fields
        accept_email = row.get('acceptMarketing', '').lower() == 'true'
        accept_whatsapp = row.get('acceptWhatsApp', '').lower() == 'true'
        accept_terms = row.get('acceptTerms', '').lower() == 'true'
        is_verified = row.get('isVerifiedSiretran', '').lower() == 'true'
        
        # Experience
        experience = metadata.get('experience', '')
        has_car = metadata.get('hasCar', '')
        credentialed = metadata.get('credentialed', '')

        # Validation
        if not external_id or not name or not phone or not state_code:
            self.stdout.write(self.style.WARNING(f'Skipping incomplete row: {external_id}'))
            return 'skipped'

        # Get state
        try:
            state = State.objects.get(code=state_code)
        except State.DoesNotExist:
            self.stdout.write(self.style.WARNING(f'Unknown state code: {state_code}'))
            return 'skipped'

        # Resolve city
        city = None
        if city_name:
            city_qs = City.objects.filter(name__iexact=city_name, state=state)
            city = city_qs.first()
            if not city:
                self.stdout.write(self.style.WARNING(f'City not found: {city_name}/{state_code}'))
                return 'skipped'

        if dry_run:
            self.stdout.write(f'Would import: {name} - {city_name}/{state_code}')
            return 'created'

        # Check if user already exists by email or CPF
        user = None
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass
        
        if not user and cpf:
            try:
                profile = Profile.objects.get(cpf=cpf)
                user = profile.user
            except Profile.DoesNotExist:
                pass

        # Create user if doesn't exist
        if not user:
            # Generate username from name
            base_username = name.lower().replace(' ', '_')[:30]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                email=email if email else f"{username}@placeholder.com",
                first_name=name.split()[0] if name else '',
                last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
            )
            
            # Create or update Profile
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = 'INSTRUCTOR'
            profile.phone = phone
            if cpf:
                profile.cpf = cpf
            profile.save()
            
            created = True
        else:
            created = False
            # Update profile
            if hasattr(user, 'profile'):
                profile = user.profile
                if profile.role != 'INSTRUCTOR':
                    profile.role = 'INSTRUCTOR'
                if not profile.cpf and cpf:
                    profile.cpf = cpf
                if not profile.phone:
                    profile.phone = phone
                profile.save()

        # Create or update InstructorProfile
        # Set visible=True if they accepted terms, verified based on Siretran
        instructor, instructor_created = InstructorProfile.objects.update_or_create(
            user=user,
            defaults={
                'city': city,
                'is_verified': is_verified,
                'is_visible': accept_terms,  # Show if accepted terms
            }
        )
        
        # Set categories if provided
        if cnh_categories:
            categories = []
            for cat_code in cnh_categories.split(','):
                cat_code = cat_code.strip().upper()
                if cat_code and len(cat_code) == 1:
                    cat = CategoryCNH.objects.filter(code=cat_code).first()
                    if cat:
                        categories.append(cat)
            if categories:
                instructor.categories.set(categories)
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {name} - {city_name}/{state_code}'))
            return 'created'
        else:
            self.stdout.write(f'→ Updated: {name} - {city_name}/{state_code}')
            return 'updated'
