"""
URL Configuration for accounts app.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from . import views
from .forms import CustomPasswordResetForm

app_name = 'accounts'

# Rate-limited PasswordResetView (5 POST requests per hour per IP)
_RateLimitedPasswordResetView = method_decorator(
    ratelimit(key='ip', rate='5/h', method='POST', block=True),
    name='dispatch',
)(auth_views.PasswordResetView)

urlpatterns = [
    path('registrar/', views.register_view, name='register'),
    path('cadastro-sucesso/', views.registration_success_view, name='registration_success'),
    path('entrar/', views.login_view, name='login'),
    path('sair/', views.logout_view, name='logout'),
    path('painel/', views.dashboard_view, name='dashboard'),
    path('perfil/editar/', views.profile_edit_view, name='profile_edit'),
    path('completar-cadastro/', views.complete_profile_view, name='complete_profile'),
    path('completar-dados-aluno/', views.complete_student_data_view, name='complete_student_data'),

    # ── Password Reset (4 steps) ──────────────────────────────────────────────
    path(
        'senha/recuperar/',
        _RateLimitedPasswordResetView.as_view(
            template_name='accounts/password_reset.html',
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
            form_class=CustomPasswordResetForm,
            success_url='/contas/senha/recuperar/enviado/',
        ),
        name='password_reset',
    ),
    path(
        'senha/recuperar/enviado/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'senha/redefinir/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url='/contas/senha/redefinir/concluido/',
        ),
        name='password_reset_confirm',
    ),
    path(
        'senha/redefinir/concluido/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
]
