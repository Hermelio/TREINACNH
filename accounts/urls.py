"""
URL Configuration for accounts app.
"""
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'accounts'

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
    # Logic (rate-limit, logging, canonical-domain injection) lives in the
    # custom CBVs defined in accounts/views.py.
    path(
        'senha/recuperar/',
        views.PasswordResetRequestView.as_view(),
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
        views.PasswordResetConfirmLoggingView.as_view(),
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
