"""
Django settings for TREINACNH project.
Production-ready configuration with security best practices.
"""
import os
from pathlib import Path
from decouple import config, Csv

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production-123456789')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# CSRF Trusted Origins - Required for forms to work with specific domains/IPs
CSRF_TRUSTED_ORIGINS = [
    'http://72.61.36.89:8080',
    'http://72.61.36.89',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third-party
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
    
    # Local apps
    'accounts.apps.AccountsConfig',
    'marketplace.apps.MarketplaceConfig',
    'verification.apps.VerificationConfig',
    'reviews.apps.ReviewsConfig',
    'billing.apps.BillingConfig',
    'core.apps.CoreConfig',
]

# Django Debug Toolbar (comentado para produção)
# if DEBUG:
#     INSTALLED_APPS += ['debug_toolbar']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_ratelimit.middleware.RatelimitMiddleware',  # Rate limiting
    'core.middleware.SecurityMiddleware',  # Custom security middleware
]

# Django Debug Toolbar Middleware (comentado para produção)
# if DEBUG:
#     MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'core.context_processors.site_settings',  # Site configuration
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database - MySQL (Corporativo)
USE_SQLITE = config('USE_SQLITE', default=False, cast=bool)

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': config('DB_HOST', default='10.54.4.7'),
            'PORT': config('DB_PORT', default='3306'),
            'NAME': config('DB_NAME', default='Raio_X'),
            'USER': config('DB_USER', default='integrador'),
            'PASSWORD': config('DB_PASSWORD', default='crystalcomgas'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            },
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Site Configuration
SITE_NAME = 'TreinaCNH'
SITE_LOGO = 'images/logos/logotipoTreinaCNH-640w.avif'  # Path relativo a STATIC_URL
SITE_URL = config('SITE_URL', default='http://localhost:8000')

# Mercado Pago Configuration
MERCADOPAGO_PUBLIC_KEY = config('MERCADOPAGO_PUBLIC_KEY', default='')
MERCADOPAGO_ACCESS_TOKEN = config('MERCADOPAGO_ACCESS_TOKEN', default='')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:dashboard'
LOGOUT_REDIRECT_URL = 'core:home'

# Crispy Forms (Bootstrap 5)
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Security Settings (Production)
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)  # Changed to False for HTTP
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)  # Changed to False for HTTP
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)  # Changed to False for HTTP
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)  # Disabled for HTTP
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_REFERRER_POLICY = 'same-origin'

# Additional Security Settings
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript access to CSRF cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = False  # Only save when modified

# Rate Limiting Configuration
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_VIEW = 'core.views.ratelimit_error'  # Custom rate limit error page

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644  # Secure file permissions
ALLOWED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx']

# Cache Configuration (for rate limiting and performance)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'treinacnh-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Debug Toolbar
if DEBUG:
    INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Custom settings
MAX_PROFILE_COMPLETION_SCORE = 100
WHATSAPP_MESSAGE_TEMPLATE = "Olá! Vi seu perfil no TREINACNH e gostaria de agendar aulas de direção."
