"""
Models for marketplace app - Cities, Instructors, Categories, and Leads.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse


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
    
    @property
    def profile_completion_score(self):
        """
        Calculate profile completion percentage (0-100).
        Used to encourage instructors to complete their profiles.
        """
        score = 0
        total_fields = 15
        
        # Basic info (3 points each)
        if self.bio:
            score += 3
        if self.neighborhoods_text:
            score += 3
        if self.age:
            score += 3
        
        # Professional (4 points each)
        if self.years_experience > 0:
            score += 4
        if self.categories.exists():
            score += 4
        if self.base_price_per_hour:
            score += 4
        
        # Vehicle (3 points each)
        if self.has_own_car and self.car_model:
            score += 6
        elif not self.has_own_car:
            score += 3
        
        # Availability (2 points each)
        if self.available_morning or self.available_afternoon or self.available_evening:
            score += 6
        
        # Avatar from user profile (5 points)
        if hasattr(self.user, 'profile') and self.user.profile.avatar:
            score += 5
        
        # Phone/WhatsApp (5 points)
        if hasattr(self.user, 'profile') and self.user.profile.whatsapp_number:
            score += 5
        
        # Verification (10 points bonus)
        if self.is_verified:
            score += 10
        
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
    CLOSED = 'CLOSED', 'Fechado'
    SPAM = 'SPAM', 'Spam'


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
    external_id = models.CharField('ID Externo', max_length=100, unique=True, help_text='ID original do lead')
    name = models.CharField('Nome', max_length=200)
    phone = models.CharField('Telefone', max_length=20)
    email = models.EmailField('Email', blank=True)
    city = models.CharField('Cidade', max_length=100)
    
    # State relation
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name='student_leads',
        verbose_name='Estado'
    )
    
    # CNH info
    category = models.CharField(
        'Categoria CNH',
        max_length=3,
        help_text='Categoria desejada: A, B, AB, etc.'
    )
    has_theory = models.BooleanField('Tem teoria', default=False, help_text='Já possui parte teórica')
    
    # Marketing preferences
    accept_marketing = models.BooleanField('Aceita marketing', default=False)
    accept_whatsapp = models.BooleanField('Aceita WhatsApp', default=False)
    accept_terms = models.BooleanField('Aceitou termos', default=False)
    
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
        return f"{self.name} - {self.city}/{self.state.code} - Cat. {self.category}"
    
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
