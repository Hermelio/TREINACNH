"""
Management command to create test instructors (2 per state).
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from marketplace.models import State, City, InstructorProfile, CategoryCNH
from accounts.models import Profile
import random


class Command(BaseCommand):
    help = 'Cria instrutores de teste (2 por estado)'

    def handle(self, *args, **options):
        """Create test instructors"""
        
        # List of instructor names
        first_names = [
            'João', 'Maria', 'Pedro', 'Ana', 'Carlos', 'Juliana', 'Rafael', 'Fernanda',
            'Lucas', 'Camila', 'Ricardo', 'Patricia', 'Bruno', 'Amanda', 'Felipe', 'Daniela',
            'Gustavo', 'Leticia', 'Rodrigo', 'Beatriz', 'Marcelo', 'Gabriela', 'Thiago', 'Bruna',
            'Leonardo', 'Larissa', 'Diego', 'Mariana', 'Vinicius', 'Carolina', 'Matheus', 'Isabela',
            'Andre', 'Vanessa', 'Fabio', 'Renata', 'Paulo', 'Cristina', 'Roberto', 'Sandra',
            'Alexandre', 'Tatiana', 'Claudio', 'Monica', 'Sergio', 'Claudia', 'Eduardo', 'Lucia',
            'Fernando', 'Adriana', 'Antonio', 'Silvia', 'Jose', 'Regina'
        ]
        
        last_names = [
            'Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Alves', 'Pereira',
            'Lima', 'Gomes', 'Costa', 'Ribeiro', 'Martins', 'Carvalho', 'Almeida', 'Lopes',
            'Soares', 'Fernandes', 'Vieira', 'Barbosa', 'Rocha', 'Dias', 'Nascimento', 'Araujo',
            'Cunha', 'Pinto', 'Teixeira', 'Correia', 'Castro', 'Cardoso'
        ]
        
        bios = [
            "Instrutor experiente com mais de 10 anos de atuação. Especialista em primeira habilitação.",
            "Profissional dedicado com excelente índice de aprovação. Aulas práticas e teóricas.",
            "Ensino paciente e personalizado. Foco em segurança e confiança ao volante.",
            "Instrutor certificado com metodologia moderna. Preparo completo para o exame.",
            "Experiência com alunos iniciantes e reciclagem. Horários flexíveis.",
            "Aulas dinâmicas e eficientes. Ajudo você a conquistar sua CNH rapidamente.",
        ]
        
        # Get all states with cities
        states = State.objects.prefetch_related('cities').all()
        categories = list(CategoryCNH.objects.all()[:3])  # A, B, AB
        
        created_count = 0
        
        for state in states:
            # Get cities for this state
            cities = list(state.cities.filter(is_active=True))
            
            if not cities:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Estado {state.code} não tem cidades ativas')
                )
                continue
            
            # Create 2 instructors per state
            for i in range(2):
                # Random name
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                username = f"{first_name.lower()}.{last_name.lower()}.{state.code.lower()}{i+1}"
                
                # Check if user already exists
                if User.objects.filter(username=username).exists():
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Usuário {username} já existe')
                    )
                    continue
                
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@treinacnh.com.br",
                    password='instrutor123',
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Update profile to instructor
                profile = user.profile
                profile.role = 'INSTRUCTOR'
                profile.phone = f'+5511{random.randint(90000, 99999)}{random.randint(1000, 9999)}'
                profile.save()
                
                # Random city from state
                city = random.choice(cities)
                
                # Generate coordinates near the state capital (with small random offset)
                lat = float(state.latitude) + random.uniform(-0.5, 0.5)
                lng = float(state.longitude) + random.uniform(-0.5, 0.5)
                
                # Create instructor profile
                instructor = InstructorProfile.objects.create(
                    user=user,
                    city=city,
                    bio=random.choice(bios),
                    years_experience=random.randint(3, 15),
                    base_price_per_hour=random.choice([80, 90, 100, 110, 120, 130]),
                    is_visible=True,
                    is_verified=True,
                    latitude=lat,
                    longitude=lng,
                    address_street=f"Rua {random.choice(['das Flores', 'Principal', 'Central', 'do Comércio', 'da Paz'])}, {random.randint(100, 999)}",
                    address_neighborhood=random.choice(['Centro', 'Jardim América', 'Vila Nova', 'Boa Vista', 'São João']),
                    address_zip=f"{random.randint(10000, 99999)}-{random.randint(100, 999)}",
                    has_own_car=True,
                    car_model=random.choice(['Gol', 'Onix', 'HB20', 'Polo', 'Argo', 'Ka']),
                    available_morning=True,
                    available_afternoon=True,
                    available_evening=random.choice([True, False])
                )
                
                # Add random categories
                instructor.categories.add(*random.sample(categories, k=random.randint(1, 2)))
                
                created_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ {first_name} {last_name} - {city.name}/{state.code} (lat: {lat:.2f}, lng: {lng:.2f})'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Concluído! {created_count} instrutores criados.')
        )
        self.stdout.write(
            self.style.WARNING('📝 Senha padrão: instrutor123')
        )
