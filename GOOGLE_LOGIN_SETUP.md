# 🔐 Configuração de Login com Google - TREINACNH

## 📋 Passo a Passo Completo

### 1. Instalar Dependências

```bash
pip install django-allauth
```

Adicionar ao `requirements.txt`:
```
django-allauth==0.61.1
```

---

## 2. ✅ Configurar Google OAuth 2.0 - JÁ CONCLUÍDO!

### ✅ Projeto criado no Google Cloud Console
- **Nome**: TREINACNH
- **Tipo**: Externo
- **Status**: Ativo

### ✅ Cliente OAuth 2.0 criado
- **Nome**: TREINACNH Web Client
- **Tipo**: Web application
- **Client ID e Secret**: Já gerados

### ✅ URLs Configuradas

**JavaScript origins autorizadas:**
```
http://localhost:8000
http://127.0.0.1:8000
https://treinacnh.com.br
```

**URIs de redirecionamento autorizadas (django-allauth):**
```
http://localhost:8000/contas/google/login/callback/
http://127.0.0.1:8000/contas/google/login/callback/
https://treinacnh.com.br/contas/google/login/callback/
```

### ℹ️ Notas Importantes
- **Google+ API não existe mais** - OAuth funciona com Google Auth Platform
- **Nenhuma API extra precisa ser ativada**
- Client ID e Secret já estão prontos para uso

---

## 3. Configurar Django Settings

### 3.1. Atualizar `config/settings.py`

Adicionar ao `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ... apps existentes ...
    
    # django-allauth (ORDEM IMPORTANTE!)
    'django.contrib.sites',  # Obrigatório
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    
    # ... resto dos apps ...
]
```

Adicionar configurações no final do arquivo:
```python
# ==========================================
# DJANGO-ALLAUTH CONFIGURATION
# ==========================================

SITE_ID = 1

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Django padrão
    'allauth.account.auth_backends.AuthenticationBackend',  # Allauth
]

# Allauth Settings
ACCOUNT_AUTHENTICATION_METHOD = 'email'  # Login com e-mail
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False  # Não obrigar username
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # Verificação opcional
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

# Redirect URLs
LOGIN_REDIRECT_URL = '/contas/dashboard/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
SOCIALACCOUNT_LOGIN_ON_GET = True  # Login automático com Google

# Social Account Settings
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'optional'
SOCIALACCOUNT_QUERY_EMAIL = True

# Google Provider Specific
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID', default=''),
            'secret': config('GOOGLE_CLIENT_SECRET', default=''),
            'key': ''
        }
    }
}

# Adapter personalizado para criar Profile automaticamente
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'
```

---

## 4. Configurar Variáveis de Ambiente

### 4.1. Arquivo `.env` (Local)

Adicionar:
```env
GOOGLE_CLIENT_ID=seu_client_id_aqui.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-seu_secret_aqui
```

### 4.2. Servidor de Produção

```bash
ssh root@72.61.36.89
cd /var/www/TREINACNH
nano .env
```

Adicionar as mesmas variáveis no `.env` do servidor.

---

## 5. Criar Adapter Personalizado

Criar arquivo `accounts/adapters.py`:

```python
"""
Custom adapters for django-allauth to integrate with our Profile system.
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to handle social account signup.
    Creates Profile automatically when user signs up via Google.
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Called before social login/signup.
        Links existing email accounts.
        """
        # If user exists with this email, connect the account
        if sociallogin.is_existing:
            return
        
        # Check if email already exists
        if sociallogin.email_addresses:
            email = sociallogin.email_addresses[0].email
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            try:
                user = User.objects.get(email=email)
                # Connect this social account to existing user
                sociallogin.connect(request, user)
                messages.info(request, 'Sua conta Google foi conectada com sucesso!')
            except User.DoesNotExist:
                pass
    
    def populate_user(self, request, sociallogin, data):
        """
        Populate user information from social account.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Get data from Google
        if sociallogin.account.provider == 'google':
            # Get first name and last name
            first_name = data.get('given_name', '')
            last_name = data.get('family_name', '')
            
            user.first_name = first_name
            user.last_name = last_name
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save user and create Profile.
        """
        user = super().save_user(request, sociallogin, form)
        
        # Profile is created automatically by signal in accounts/models.py
        # But we ensure it exists
        from accounts.models import Profile
        profile, created = Profile.objects.get_or_create(user=user)
        
        if created:
            # Set default role based on request parameter or context
            # By default, Google login users are students (not instructors)
            profile.is_instructor = False
            profile.save()
        
        return user
```

---

## 6. Atualizar URLs

### 6.1. `config/urls.py`

Adicionar as rotas do allauth:
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Allauth URLs (IMPORTANTE: antes das accounts!)
    path('contas/', include('allauth.urls')),
    
    # Apps existentes
    path('contas/', include('accounts.urls')),
    path('instrutores/', include('marketplace.urls')),
    path('verificacao/', include('verification.urls')),
    path('avaliacoes/', include('reviews.urls')),
    path('planos/', include('billing.urls')),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 7. Atualizar Templates

### 7.1. `templates/accounts/login.html`

Adicionar botão do Google após o formulário:

```html
{% extends 'base.html' %}
{% load socialaccount %}

{% block content %}
<div class="container py-5" style="padding-top: 7rem !important;">
    <div class="row justify-content-center">
        <div class="col-md-5">
            <div class="card shadow">
                <div class="card-body p-5">
                    <h2 class="text-center mb-4" style="color: #000000;">Entrar</h2>
                    
                    <!-- Botão Login com Google -->
                    <a href="{% provider_login_url 'google' %}" 
                       class="btn btn-outline-danger w-100 mb-3 d-flex align-items-center justify-content-center"
                       style="border-width: 2px;">
                        <svg width="18" height="18" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" class="me-2">
                            <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                            <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                            <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                            <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                        </svg>
                        Continuar com Google
                    </a>
                    
                    <div class="text-center my-3">
                        <span class="text-muted">ou</span>
                    </div>
                    
                    {% if form.non_field_errors %}
                        <div class="alert alert-danger">
                            {{ form.non_field_errors }}
                        </div>
                    {% endif %}
                    
                    <form method="post" novalidate>
                        {% csrf_token %}
                        
                        <div class="mb-3">
                            <label for="id_username" class="form-label">{{ form.username.label }}</label>
                            {{ form.username }}
                            {% if form.username.errors %}
                                <div class="text-danger small">{{ form.username.errors }}</div>
                            {% endif %}
                        </div>
                        
                        <div class="mb-3">
                            <label for="id_password" class="form-label">{{ form.password.label }}</label>
                            {{ form.password }}
                            {% if form.password.errors %}
                                <div class="text-danger small">{{ form.password.errors }}</div>
                            {% endif %}
                        </div>
                        
                        <button type="submit" class="btn btn-primary w-100 mb-3">
                            <i class="bi bi-box-arrow-in-right me-2"></i>Entrar
                        </button>
                    </form>
                    
                    <hr class="my-4">
                    <p class="text-center mb-0">
                        Não tem uma conta? <a href="{% url 'accounts:register' %}">Cadastre-se</a>
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### 7.2. `templates/accounts/register.html`

Adicionar botão do Google no topo:

```html
{% load socialaccount %}

<!-- Adicionar logo após o título -->
<h2 class="text-center mb-4" style="color: #000000;">Criar Conta</h2>

<!-- Botão Login com Google -->
<a href="{% provider_login_url 'google' %}" 
   class="btn btn-outline-danger w-100 mb-3 d-flex align-items-center justify-content-center"
   style="border-width: 2px;">
    <svg width="18" height="18" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" class="me-2">
        <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
        <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
        <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
        <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
    </svg>
    Cadastrar com Google
</a>

<div class="text-center my-3">
    <span class="text-muted">ou preencha o formulário</span>
</div>
```

---

## 8. Executar Migrations

```bash
# Local
python manage.py migrate

# Servidor
ssh root@72.61.36.89
cd /var/www/TREINACNH
source venv/bin/activate
python manage.py migrate
```

---

## 9. Configurar no Admin Django

1. Acesse: `/admin/sites/site/`
2. Edite o Site com ID=1:
   - **Domain name**: `treinacnh.com.br` (ou seu domínio)
   - **Display name**: `TREINACNH`

3. Acesse: `/admin/socialaccount/socialapp/`
4. Clique em **Add Social Application**:
   - **Provider**: Google
   - **Name**: Google OAuth
   - **Client ID**: Cole o Client ID do Google
   - **Secret key**: Cole o Client Secret do Google
   - **Sites**: Selecione o site "treinacnh.com.br"
   - Clique em **Save**

---

## 10. Testar Localmente

1. Inicie o servidor:
   ```bash
   python manage.py runserver
   ```

2. Acesse: `http://localhost:8000/contas/login/`

3. Clique no botão "Continuar com Google"

4. Faça login com sua conta Google

5. Verifique se foi criado:
   - User no Django
   - Profile associado
   - Login funcionando

---

## 11. Deploy para Produção

```bash
# 1. Atualizar requirements.txt localmente
pip freeze > requirements.txt

# 2. Commit e push
git add .
git commit -m "feat: Adiciona login com Google usando django-allauth"
git push origin main

# 3. Atualizar servidor
ssh root@72.61.36.89
cd /var/www/TREINACNH
git pull origin main

# 4. Instalar dependências
source venv/bin/activate
pip install -r requirements.txt

# 5. Atualizar .env com credenciais do Google
nano .env
# Adicionar:
# GOOGLE_CLIENT_ID=seu_client_id.apps.googleusercontent.com
# GOOGLE_CLIENT_SECRET=GOCSPX-seu_secret

# 6. Executar migrations
python manage.py migrate

# 7. Collectstatic
python manage.py collectstatic --no-input

# 8. Reiniciar serviço
sudo systemctl restart gunicorn-treinacnh.service
sudo systemctl reload nginx
```

---

## 12. Verificar Admin

1. Acesse: `http://72.61.36.89:8080/admin/`
2. Vá em **Sites > Sites**
3. Edite para colocar o domínio correto
4. Vá em **Social applications**
5. Adicione o Google OAuth com as credenciais

---

## ✅ Checklist Final

- [ ] django-allauth instalado
- [ ] Projeto criado no Google Cloud Console
- [ ] Google+ API ativada
- [ ] Credenciais OAuth criadas
- [ ] URLs de redirecionamento configuradas
- [ ] Client ID e Secret no .env
- [ ] Settings.py atualizado
- [ ] Adapter personalizado criado
- [ ] URLs atualizadas
- [ ] Templates atualizados com botão Google
- [ ] Migrations executadas
- [ ] Site configurado no admin
- [ ] Social App configurada no admin
- [ ] Testado localmente
- [ ] Deploy em produção
- [ ] Testado em produção

---

## 🎯 Benefícios

✅ **Cadastro mais rápido**: Usuários podem se registrar com 1 clique  
✅ **Mais seguro**: Google gerencia autenticação  
✅ **Menos senha para lembrar**: Usuários adoram  
✅ **Maior taxa de conversão**: Menos fricção no cadastro  
✅ **E-mail verificado**: Google já verifica o e-mail  
✅ **Foto de perfil**: Pode importar foto do Google automaticamente

---

## 🐛 Troubleshooting

### Erro: "Redirect URI mismatch"
**Solução**: Verifique se a URI no Google Console está exatamente igual à configurada.

### Erro: "Site matching query does not exist"
**Solução**: Execute `python manage.py migrate` e configure o Site no admin.

### Erro: "SocialApp matching query does not exist"
**Solução**: Configure o Social App no admin Django.

### Botão Google não aparece
**Solução**: Verifique se carregou `{% load socialaccount %}` no template.

---

## 📞 Suporte

Se tiver dúvidas, consulte:
- Documentação django-allauth: https://django-allauth.readthedocs.io/
- Google OAuth 2.0: https://developers.google.com/identity/protocols/oauth2
