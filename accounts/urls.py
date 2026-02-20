"""
URL Configuration for accounts app.
"""
from django.urls import path
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
]
