"""
Models for marketplace app - Cities, Instructors, Categories, and Leads.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone


class State(models.Model):
    """Brazilian states (UF)"""
    code = models.CharField('UF', max_length=2, unique=True, help_text='Sigla do Estado (ex: SP)')
    name = models.CharField('Nome', max_length=100)
    latitude = models.DecimalField(
        'Latitude',
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Latitude da capital do estado'
    )
    longitude = models.DecimalField(
        'Longitude',
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Longitude da capital do estado'
    )
    
    class Meta:
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class City(models.Model):
    """Cities with state relationship"""
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities', verbose_name='Estado')
    name = models.CharField('Nome', max_length=100)
    slug = models.SlugField('Slug', max_length=120, unique=True, blank=True)
    is_active = models.BooleanField('Ativo', default=True, help_text='Cidade disponível no marketplace')
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'
        ordering = ['state', 'name']
        unique_together = [['state', 'name']]
        indexes = [
            models.Index(fields=['state', 'name']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return f"{self.name}/{self.state.code}"
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name and state"""
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.state.code}")
            self.slug = base_slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """URL for city listing page"""
        return reverse('marketplace:city_list', kwargs={'state_code': self.state.code, 'city_slug': self.slug})
    
    @property
    def instructor_count(self):
        """Count active and visible instructors in this city"""
        return self.instructors.filter(is_visible=True, is_verified=True).count()


class CityGeoCache(models.Model):
    """Cache for city geocoding to avoid repeated API calls"""
    city_key = models.CharField(
        'Chave Cidade',
        max_length=200,
        unique=True,
        db_index=True,
        help_text='Formato: cidade_normalizada|UF'
    )
    city_name = models.CharField('Cidade', max_length=100)
    state_code = models.CharField('UF', max_length=2)
    latitude = models.DecimalField('Latitude', max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField('Longitude', max_digits=9, decimal_places=6, null=True, blank=True)
    provider = models.CharField(
        'Provedor',
        max_length=50,
        blank=True,
        help_text='API de geocoding usada (nominatim, google, manual, etc.)'
    )
    geocoded = models.BooleanField('Geocodificado', default=False)
    failed = models.BooleanField('Falhou', default=False, help_text='Geocoding falhou')
    attempts = models.IntegerField('Tentativas', default=0)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Cache de Geocoding'
        verbose_name_plural = 'Cache de Geocoding'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['city_key']),
            models.Index(fields=['state_code', 'city_name']),
            models.Index(fields=['geocoded']),
        ]
    
    def __str__(self):
        status = '✓' if self.geocoded else ('✗' if self.failed else '?')
        return f"{status} {self.city_name}/{self.state_code}"
    
    @staticmethod
    def normalize_city_key(city_name, state_code):
        """Create normalized key for city"""
        import unicodedata
        # Remove accents and lowercase
        city_clean = unicodedata.normalize('NFKD', city_name).encode('ASCII', 'ignore').decode('ASCII')
        city_clean = city_clean.strip().lower()
        state_clean = state_code.strip().upper()
        return f"{city_clean}|{state_clean}"


class CategoryCNH(models.Model):
    """CNH categories (A, B, C, D, E)"""
    code = models.CharField('Código', max_length=1, unique=True, choices=[
        ('A', 'Categoria A - Motos'),
        ('B', 'Categoria B - Carros'),
        ('C', 'Categoria C - Caminhões'),
        ('D', 'Categoria D - Ônibus'),
        ('E', 'Categoria E - Carretas'),
    ])
    label = models.CharField('Nome', max_length=100)
    description = models.TextField('Descrição', blank=True)
    
    class Meta:
        verbose_name = 'Categoria CNH'
        verbose_name_plural = 'Categorias CNH'
        ordering = ['code']
    
    def __str__(self):
        return f"Categoria {self.code}"


class GenderChoices(models.TextChoices):
    """Gender options for instructors"""
    MALE = 'M', 'Masculino'
    FEMALE = 'F', 'Feminino'
    OTHER = 'O', 'Outro'


class InstructorProfile(models.Model):
    """
    Extended profile for instructors with professional information.
    This is separate from accounts.Profile to keep role-specific data organized.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='instructor_profile',
        verbose_name='Usuário'
    )
    city = models.ForeignKey(
        City, 
        on_delete=models.CASCADE, 
        related_name='instructors',
        verbose_name='Cidade Principal'
    )
    
    # Address and Geolocation
    address_street = models.CharField('Endereço', max_length=200, blank=True, help_text='Rua, número')
    address_neighborhood = models.CharField('Bairro', max_length=100, blank=True)
    address_zip = models.CharField('CEP', max_length=10, blank=True)
    latitude = models.DecimalField('Latitude', max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField('Longitude', max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Professional Info
    bio = models.TextField('Sobre mim', max_length=1000, blank=True, help_text='Descreva sua experiência')
    neighborhoods_text = models.CharField(
        'Bairros atendidos', 
        max_length=255, 
        blank=True,
        help_text='Ex: Centro, Jardins, Vila Mariana'
    )
    
    # Personal Info
    gender = models.CharField('Gênero', max_length=1, choices=GenderChoices.choices, default=GenderChoices.MALE)
    age = models.PositiveIntegerField(
        'Idade', 
        blank=True, 
        null=True,
        validators=[MinValueValidator(18), MaxValueValidator(100)]
    )
    years_experience = models.PositiveIntegerField(
        'Anos de experiência',
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    
    # Vehicle Info
    has_own_car = models.BooleanField('Possui carro próprio', default=False)
    car_model = models.CharField('Modelo do carro', max_length=100, blank=True)
    
    # Categories taught
    categories = models.ManyToManyField(
        CategoryCNH,
        related_name='instructors',
        verbose_name='Categorias que ensina',
        blank=True
    )
    
    # Availability
    available_morning = models.BooleanField('Disponível de manhã', default=True)
    available_afternoon = models.BooleanField('Disponível à tarde', default=True)
    available_evening = models.BooleanField('Disponível à noite', default=False)
    
    # Pricing (optional)
    base_price_per_hour = models.DecimalField(
        'Preço base por hora',
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Valor aproximado (opcional)'
    )
    price_notes = models.CharField(
        'Observações sobre preço',
        max_length=255,
        blank=True,
        help_text='Ex: Preço por pacote de 10 aulas'
    )
    
    # Status
    is_visible = models.BooleanField(
        'Visível no marketplace',
        default=True,
        help_text='Desmarque para pausar temporariamente seu perfil'
    )
    is_verified = models.BooleanField(
        'Verificado',
        default=False,
        help_text='Instrutor com documentos aprovados'
    )
    
    # Statistics
    total_students = models.PositiveIntegerField(
        'Total de Alunos',
        default=0,
        help_text='Número de alunos que finalizaram aulas'
    )
    average_rating = models.DecimalField(
        'Média de Avaliações',
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Média de avaliações (1.00 a 5.00)'
    )
    total_reviews = models.PositiveIntegerField(
        'Total de Avaliações',
        default=0,
        help_text='Número total de avaliações recebidas'
    )
    
    # Trial Period (14 days free)
    trial_start_date = models.DateTimeField(
        'Data de Início do Trial',
        null=True,
        blank=True,
        help_text='Data em que o trial de 14 dias começou'
    )
    trial_end_date = models.DateTimeField(
        'Data de Fim do Trial',
        null=True,
        blank=True,
        help_text='Data em que o trial de 14 dias termina'
    )
    is_trial_active = models.BooleanField(
        'Trial Ativo',
        default=False,
        help_text='Instrutor está no período de trial gratuito'
    )
    trial_expiration_notified_7d = models.BooleanField(
        'Notificado 7 dias antes',
        default=False,
        help_text='E-mail de aviso 7 dias antes enviado'
    )
    trial_expiration_notified_3d = models.BooleanField(
        'Notificado 3 dias antes',
        default=False,
        help_text='E-mail de aviso 3 dias antes enviado'
    )
    trial_expiration_notified_1d = models.BooleanField(
        'Notificado 1 dia antes',
        default=False,
        help_text='E-mail de aviso 1 dia antes enviado'
    )
    trial_blocked_notified = models.BooleanField(
        'Notificado ao Bloquear',
        default=False,
        help_text='E-mail de bloqueio enviado'
    )
    
    # Metadata
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Instrutor'
        verbose_name_plural = 'Perfis de Instrutores'
        ordering = ['-is_verified', '-created_at']
        indexes = [
            models.Index(fields=['city', 'is_visible', 'is_verified']),
            models.Index(fields=['gender']),
            models.Index(fields=['has_own_car']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.city}"
    
    def get_absolute_url(self):
        """URL for instructor detail page"""
        return reverse('marketplace:instructor_detail', kwargs={'pk': self.pk})
    
    def activate_trial(self):
        """Activate 14-day free trial"""
        from django.utils import timezone
        from datetime import timedelta
        
        if not self.trial_start_date:
            self.trial_start_date = timezone.now()
            self.trial_end_date = self.trial_start_date + timedelta(days=14)
            self.is_trial_active = True
            self.is_visible = True
            self.save()
    
    def days_until_trial_end(self):
        """Calculate days remaining in trial"""
        if not self.trial_end_date:
            return None
        from django.utils import timezone
        delta = self.trial_end_date - timezone.now()
        return delta.days
    
    def is_trial_expired(self):
        """Check if trial period has expired"""
        if not self.trial_end_date or not self.is_trial_active:
            return False
        from django.utils import timezone
        return timezone.now() > self.trial_end_date
    
    @property
    def profile_completion_score(self):
        """
        Calculate profile completion percentage (0-100).

        Breakdown (total = 100):
          Bio                          10
          Bairros / área de atuação    10
          Idade                         5
          Anos de experiência           5
          Categorias (A, B…)           10
          Preço base por hora          10
          Informação de veículo         5
          Disponibilidade               10
          Avatar                        10
          WhatsApp                     10
          Documento aprovado (CNH ou
            Certificado DETRAN)        15
          ─────────────────────────── ───
          TOTAL                        100
        """
        score = 0

        # ── Informações básicas ───────────────────────────────────────
        if self.bio:
            score += 10
        if self.neighborhoods_text:
            score += 10
        if self.age:
            score += 5

        # ── Dados profissionais ───────────────────────────────────────
        if self.years_experience and self.years_experience > 0:
            score += 5
        if self.categories.exists():
            score += 10
        if self.base_price_per_hour:
            score += 10

        # ── Veículo ───────────────────────────────────────────────────
        if self.has_own_car and self.car_model:
            score += 5
        elif not self.has_own_car:
            score += 5   # informou que não tem carro próprio

        # ── Disponibilidade ───────────────────────────────────────────
        if self.available_morning or self.available_afternoon or self.available_evening:
            score += 10

        # ── Contato / foto ────────────────────────────────────────────
        if hasattr(self.user, 'profile') and self.user.profile.avatar:
            score += 10
        if hasattr(self.user, 'profile') and self.user.profile.whatsapp_number:
            score += 10

        # ── Documento aprovado (CNH OU Certificado DETRAN) ────────────
        # Obrigatório para atingir 100 %
        has_approved_doc = self.documents.filter(
            doc_type__in=['CNH', 'CERT_INSTRUTOR'],
            status='APPROVED'
        ).exists()
        if has_approved_doc:
            score += 15

        return min(score, 100)
    
    @property
    def badges(self):
        """Return list of badges for this instructor"""
        badge_list = []
        
        if self.is_verified:
            badge_list.append({'name': 'Verificado', 'class': 'success', 'icon': 'bi-patch-check-fill'})
        
        # New instructor (created in last 30 days)
        from django.utils import timezone
        from datetime import timedelta
        if self.created_at > timezone.now() - timedelta(days=30):
            badge_list.append({'name': 'Novo', 'class': 'info', 'icon': 'bi-star-fill'})
        
        # Experienced (5+ years)
        if self.years_experience >= 5:
            badge_list.append({'name': 'Experiente', 'class': 'warning', 'icon': 'bi-award-fill'})
        
        # Has own car
        if self.has_own_car:
            badge_list.append({'name': 'Carro Próprio', 'class': 'primary', 'icon': 'bi-car-front-fill'})
        
        return badge_list
    
    def update_statistics(self):
        """
        Update instructor statistics (average rating and total students).
        Should be called after a new review or completed lead.
        """
        from reviews.models import Review, ReviewStatusChoices
        from django.db.models import Avg, Count
        
        # Update total students (leads with COMPLETED status)
        completed_leads = Lead.objects.filter(
            instructor=self,
            status=LeadStatusChoices.COMPLETED
        ).values('student_user').distinct()
        self.total_students = completed_leads.count()
        
        # Update average rating (only published reviews)
        reviews_stats = Review.objects.filter(
            instructor=self,
            status=ReviewStatusChoices.PUBLISHED
        ).aggregate(
            avg_rating=Avg('rating'),
            total=Count('id')
        )
        
        self.average_rating = reviews_stats['avg_rating']
        self.total_reviews = reviews_stats['total'] or 0
        
        self.save(update_fields=['total_students', 'average_rating', 'total_reviews'])

    
    @property
    def availability_text(self):
        """Return human-readable availability"""
        times = []
        if self.available_morning:
            times.append('Manhã')
        if self.available_afternoon:
            times.append('Tarde')
        if self.available_evening:
            times.append('Noite')
        return ', '.join(times) if times else 'Não informado'
    
    def get_whatsapp_link(self, message=None):
        """Generate WhatsApp link for contact"""
        if not hasattr(self.user, 'profile') or not self.user.profile.whatsapp_number:
            return None
        
        # Clean phone number (remove non-digits)
        phone = ''.join(filter(str.isdigit, self.user.profile.whatsapp_number))
        
        if not message:
            message = f"Olá {self.user.first_name}! Vi seu perfil no TREINACNH e gostaria de agendar aulas de direção em {self.city}."
        
        # URL encode message
        from urllib.parse import quote
        encoded_message = quote(message)
        
        return f"https://wa.me/{phone}?text={encoded_message}"


class LeadStatusChoices(models.TextChoices):
    """Lead status options"""
    NEW = 'NEW', 'Novo'
    CONTACTED = 'CONTACTED', 'Contatado'
    SCHEDULED = 'SCHEDULED', 'Agendado'
    COMPLETED = 'COMPLETED', 'Aulas Finalizadas'
    CLOSED = 'CLOSED', 'Fechado'
    SPAM = 'SPAM', 'Spam'


class WeekdayChoices(models.IntegerChoices):
    """Weekday choices (0=Monday, 6=Sunday)"""
    MONDAY = 0, 'Segunda-feira'
    TUESDAY = 1, 'Terça-feira'
    WEDNESDAY = 2, 'Quarta-feira'
    THURSDAY = 3, 'Quinta-feira'
    FRIDAY = 4, 'Sexta-feira'
    SATURDAY = 5, 'Sábado'
    SUNDAY = 6, 'Domingo'


class Lead(models.Model):
    """
    Lead/contact request from student to instructor.
    Can be created by logged-in users or anonymous visitors.
    """
    # Relations
    student_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads_sent',
        verbose_name='Aluno (usuário)'
    )
    instructor = models.ForeignKey(
        InstructorProfile,
        on_delete=models.CASCADE,
        related_name='leads_received',
        verbose_name='Instrutor'
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Cidade'
    )
    
    # Contact Info (required even if user is logged in)
    contact_name = models.CharField('Nome', max_length=100)
    contact_phone = models.CharField('Telefone/WhatsApp', max_length=20)
    
    # CNH Category
    category = models.ForeignKey(
        CategoryCNH,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads',
        verbose_name='Categoria CNH Desejada'
    )
    
    # Request Details
    preferred_schedule = models.CharField(
        'Horário preferido',
        max_length=50,
        blank=True,
        help_text='Ex: Manhã, Tarde, Noite'
    )
    message = models.TextField('Mensagem', max_length=500, blank=True)
    
    # Status
    status = models.CharField(
        'Status',
        max_length=20,
        choices=LeadStatusChoices.choices,
        default=LeadStatusChoices.NEW
    )
    
    # Metadata
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    ip_address = models.GenericIPAddressField('IP', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Lead/Contato'
        verbose_name_plural = 'Leads/Contatos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['instructor', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.contact_name} → {self.instructor.user.get_full_name()} ({self.get_status_display()})"


class StudentLead(models.Model):
    """
    Student leads waiting for instructors in their state.
    These are potential students registered before instructors are available.
    """
    # Original data from CSV
    external_id = models.CharField('ID Externo', max_length=100, unique=True, null=True, blank=True, help_text='ID original do lead')
    
    # Personal info
    name = models.CharField('Nome', max_length=200)
    photo = models.ImageField('Foto', upload_to='students/', null=True, blank=True, help_text='Foto do aluno (opcional)')
    phone = models.CharField('WhatsApp', max_length=20)
    email = models.EmailField('Email')
    email_verified = models.BooleanField('Email Verificado', default=False)
    
    # Location
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name='student_leads',
        verbose_name='Estado'
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name='student_leads',
        verbose_name='Cidade',
        null=True,
        blank=True
    )
    
    # CNH info
    categories = models.ManyToManyField(
        CategoryCNH,
        verbose_name='Categorias Desejadas',
        related_name='student_leads',
        help_text='Categorias de CNH que deseja obter'
    )
    has_theory = models.BooleanField('Concluiu Parte Teórica', default=False, help_text='Já concluiu a parte teórica')
    
    # Marketing preferences and LGPD consents
    accept_whatsapp = models.BooleanField('Aceita WhatsApp', default=True, help_text='Aceita receber mensagens via WhatsApp')
    accept_email = models.BooleanField('Aceita Email', default=True, help_text='Aceita receber mensagens via email')
    accept_terms = models.BooleanField('Aceitou Termos', default=False, help_text='Aceitou os termos de uso')
    
    # Contact status
    is_contacted = models.BooleanField('Foi contatado', default=False)
    contacted_at = models.DateTimeField('Data do contato', null=True, blank=True)
    
    # Notification status
    notified_about_instructor = models.BooleanField(
        'Notificado sobre instrutor',
        default=False,
        help_text='Já foi notificado que há instrutor disponível no estado'
    )
    notified_at = models.DateTimeField('Data da notificação', null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField('Metadados', default=dict, blank=True, help_text='Dados adicionais do CSV')
    notes = models.TextField('Observações', blank=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Lead de Aluno'
        verbose_name_plural = 'Leads de Alunos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['state', 'notified_about_instructor']),
            models.Index(fields=['is_contacted']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        categories_str = ', '.join([cat.code for cat in self.categories.all()]) if self.categories.exists() else 'N/A'
        city_name = self.city.name if self.city else 'N/A'
        return f"{self.name} - {city_name}/{self.state.code} - Cat. {categories_str}"
    
    @property
    def has_instructor_in_state(self):
        """Check if there are verified instructors in the same state"""
        return InstructorProfile.objects.filter(
            city__state=self.state,
            is_visible=True,
            is_verified=True
        ).exists()
    
    def get_whatsapp_link(self, message=None):
        """Generate WhatsApp link for contact"""
        # Clean phone number (remove non-digits)
        phone = ''.join(filter(str.isdigit, self.phone))
        
        if not message:
            message = f"Olá {self.name.split()[0]}! Boas notícias! Agora temos instrutores disponíveis em {self.state.code}. Confira em https://treinacnh.com.br/mapa"
        
        # URL encode message
        from urllib.parse import quote
        encoded_message = quote(message)
        
        return f"https://wa.me/55{phone}?text={encoded_message}"


class InstructorAvailability(models.Model):
    """
    Weekly availability schedule for instructors.
    Defines which days and time slots the instructor is available.
    """
    instructor = models.ForeignKey(
        InstructorProfile,
        on_delete=models.CASCADE,
        related_name='availabilities',
        verbose_name='Instrutor'
    )
    weekday = models.IntegerField(
        'Dia da Semana',
        choices=WeekdayChoices.choices,
        help_text='0=Segunda, 6=Domingo'
    )
    start_time = models.TimeField('Horário Inicial')
    end_time = models.TimeField('Horário Final')
    is_active = models.BooleanField('Ativo', default=True)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Disponibilidade do Instrutor'
        verbose_name_plural = 'Disponibilidades dos Instrutores'
        ordering = ['weekday', 'start_time']
        unique_together = ['instructor', 'weekday', 'start_time']
        indexes = [
            models.Index(fields=['instructor', 'weekday', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.instructor.user.get_full_name()} - {self.get_weekday_display()} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"
    
    def clean(self):
        """Validate that start_time is before end_time"""
        from django.core.exceptions import ValidationError
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('Horário inicial deve ser anterior ao horário final.')


class Appointment(models.Model):
    """
    Scheduled appointment/lesson between student and instructor.
    Blocks specific time slots in instructor's schedule.
    """
    # Relations
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Lead'
    )
    instructor = models.ForeignKey(
        InstructorProfile,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Instrutor'
    )
    student_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments',
        verbose_name='Aluno'
    )
    
    # Appointment details
    appointment_date = models.DateField('Data da Aula')
    start_time = models.TimeField('Horário Inicial')
    end_time = models.TimeField('Horário Final')
    duration_hours = models.DecimalField(
        'Duração (horas)',
        max_digits=3,
        decimal_places=1,
        default=1.0,
        help_text='Duração da aula em horas'
    )
    
    # Status
    is_confirmed = models.BooleanField('Confirmado', default=False)
    is_completed = models.BooleanField('Concluído', default=False)
    is_cancelled = models.BooleanField('Cancelado', default=False)
    cancellation_reason = models.TextField('Motivo do Cancelamento', blank=True)
    
    # Notes
    notes = models.TextField('Observações', blank=True, help_text='Observações sobre a aula')
    
    # Metadata
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        ordering = ['appointment_date', 'start_time']
        indexes = [
            models.Index(fields=['instructor', 'appointment_date']),
            models.Index(fields=['student_user', 'appointment_date']),
            models.Index(fields=['is_confirmed', 'is_cancelled']),
        ]
    
    def __str__(self):
        student_name = self.student_user.get_full_name() if self.student_user else self.lead.contact_name
        return f"{student_name} → {self.instructor.user.get_full_name()} - {self.appointment_date} {self.start_time.strftime('%H:%M')}"
    
    def clean(self):
        """Validate appointment"""
        from django.core.exceptions import ValidationError
        
        # Validate time range
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('Horário inicial deve ser anterior ao horário final.')
        
        # Check for overlapping appointments (only if not cancelled)
        if not self.is_cancelled and self.instructor and self.appointment_date:
            overlapping = Appointment.objects.filter(
                instructor=self.instructor,
                appointment_date=self.appointment_date,
                is_cancelled=False
            ).exclude(pk=self.pk)
            
            for appt in overlapping:
                # Check if times overlap
                if (self.start_time < appt.end_time and self.end_time > appt.start_time):
                    raise ValidationError(
                        f'Este horário conflita com outro agendamento: '
                        f'{appt.start_time.strftime("%H:%M")}-{appt.end_time.strftime("%H:%M")}'
                    )
    
    @property
    def status_display(self):
        """Human-readable status"""
        if self.is_cancelled:
            return 'Cancelado'
        if self.is_completed:
            return 'Concluído'
        if self.is_confirmed:
            return 'Confirmado'
        return 'Pendente'
