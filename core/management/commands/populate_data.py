"""
Management command to populate initial data for testing.
Usage: python manage.py populate_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from marketplace.models import State, City, CategoryCNH, InstructorProfile
from core.models import FAQEntry, StaticPage
from billing.models import Plan


class Command(BaseCommand):
    help = 'Populate database with initial test data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))

        # Create States
        self.stdout.write('Creating states...')
        sp, _ = State.objects.get_or_create(code='SP', defaults={'name': 'São Paulo'})
        rj, _ = State.objects.get_or_create(code='RJ', defaults={'name': 'Rio de Janeiro'})
        mg, _ = State.objects.get_or_create(code='MG', defaults={'name': 'Minas Gerais'})
        pr, _ = State.objects.get_or_create(code='PR', defaults={'name': 'Paraná'})
        rs, _ = State.objects.get_or_create(code='RS', defaults={'name': 'Rio Grande do Sul'})

        # Create Cities
        self.stdout.write('Creating cities...')
        cities_data = [
            (sp, 'São Paulo'),
            (sp, 'Campinas'),
            (sp, 'Santos'),
            (rj, 'Rio de Janeiro'),
            (rj, 'Niterói'),
            (mg, 'Belo Horizonte'),
            (mg, 'Uberlândia'),
            (pr, 'Curitiba'),
            (rs, 'Porto Alegre'),
        ]
        
        for state, city_name in cities_data:
            City.objects.get_or_create(
                state=state,
                name=city_name,
                defaults={'is_active': True}
            )

        # Create CNH Categories
        self.stdout.write('Creating CNH categories...')
        categories_data = [
            ('A', 'Categoria A - Motos'),
            ('B', 'Categoria B - Carros'),
            ('C', 'Categoria C - Caminhões'),
            ('D', 'Categoria D - Ônibus'),
            ('E', 'Categoria E - Carretas'),
        ]
        
        for code, label in categories_data:
            CategoryCNH.objects.get_or_create(code=code, defaults={'label': label})

        # Create Plans
        self.stdout.write('Creating plans...')
        plans_data = [
            {
                'name': 'Básico',
                'price_monthly': 0.00,
                'description': 'Cadastro gratuito',
                'features': 'Perfil público\nAté 10 leads/mês\nSuporte por email',
                'order': 1,
            },
            {
                'name': 'Premium',
                'price_monthly': 49.90,
                'description': 'Ideal para instrutores ativos',
                'features': 'Tudo do Básico\nLeads ilimitados\nDestaque na busca\nSuporte prioritário\nBadge Premium',
                'order': 2,
            },
            {
                'name': 'Profissional',
                'price_monthly': 99.90,
                'description': 'Para quem quer máxima visibilidade',
                'features': 'Tudo do Premium\nDestaque em várias cidades\nPosição de topo\nRelatórios avançados\nGerente de conta',
                'order': 3,
            },
        ]
        
        for plan_data in plans_data:
            Plan.objects.get_or_create(name=plan_data['name'], defaults=plan_data)

        # Create FAQ Entries
        self.stdout.write('Creating FAQ entries...')
        faqs_data = [
            {
                'question': 'Como funciona o TREINACNH?',
                'answer': 'O TREINACNH é uma plataforma que conecta alunos e instrutores de direção. Você busca por cidade, filtra instrutores e entra em contato diretamente via WhatsApp.',
                'category': 'GENERAL',
                'order': 1,
            },
            {
                'question': 'O cadastro é gratuito?',
                'answer': 'Sim! Tanto alunos quanto instrutores podem se cadastrar gratuitamente.',
                'category': 'GENERAL',
                'order': 2,
            },
            {
                'question': 'Como encontro um instrutor?',
                'answer': 'Acesse a página de cidades, escolha sua localidade e use os filtros para encontrar o instrutor ideal.',
                'category': 'STUDENT',
                'order': 1,
            },
            {
                'question': 'Como funciona a verificação?',
                'answer': 'Todos os instrutores passam por análise de documentos (CNH e certificado). Instrutores verificados recebem um selo.',
                'category': 'STUDENT',
                'order': 2,
            },
            {
                'question': 'Como me cadastro como instrutor?',
                'answer': 'Clique em "Cadastrar" no menu, escolha "Instrutor" e preencha seus dados. Depois, complete seu perfil profissional.',
                'category': 'INSTRUCTOR',
                'order': 1,
            },
            {
                'question': 'Preciso pagar para me cadastrar?',
                'answer': 'Não! O cadastro básico é gratuito. Temos planos pagos opcionais com benefícios extras.',
                'category': 'INSTRUCTOR',
                'order': 2,
            },
        ]
        
        for faq_data in faqs_data:
            FAQEntry.objects.get_or_create(
                question=faq_data['question'],
                defaults=faq_data
            )

        # Create Static Pages
        self.stdout.write('Creating static pages...')
        pages_data = [
            {
                'title': 'Termos de Uso',
                'slug': 'termos',
                'content': '<h3>1. Aceitação dos Termos</h3><p>Ao acessar e usar o TREINACNH, você concorda com estes termos.</p><h3>2. Responsabilidades</h3><p>O TREINACNH é uma plataforma de conexão. A negociação e execução das aulas é responsabilidade exclusiva de alunos e instrutores.</p><h3>3. Uso Adequado</h3><p>É proibido usar a plataforma para fins ilícitos ou fraudulentos.</p>',
            },
            {
                'title': 'Política de Privacidade',
                'slug': 'privacidade',
                'content': '<h3>1. Coleta de Dados</h3><p>Coletamos informações básicas como nome, email e telefone para funcionamento da plataforma.</p><h3>2. Uso dos Dados</h3><p>Seus dados são usados apenas para operação da plataforma e não são compartilhados com terceiros sem autorização.</p><h3>3. Segurança</h3><p>Implementamos medidas de segurança para proteger seus dados.</p>',
            },
        ]
        
        for page_data in pages_data:
            StaticPage.objects.get_or_create(slug=page_data['slug'], defaults=page_data)

        self.stdout.write(self.style.SUCCESS('✓ Data population completed successfully!'))
        self.stdout.write(self.style.WARNING('\nNext steps:'))
        self.stdout.write('1. Create a superuser: python manage.py createsuperuser')
        self.stdout.write('2. Run server: python manage.py runserver')
        self.stdout.write('3. Access admin: http://localhost:8000/admin')
