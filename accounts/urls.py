"""
URL Configuration for accounts app.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('registrar/', views.register_view, name='register'),
    path('entrar/', views.login_view, name='login'),
    path('sair/', views.logout_view, name='logout'),
    path('painel/', views.dashboard_view, name='dashboard'),
    path('perfil/editar/', views.profile_edit_view, name='profile_edit'),
]
