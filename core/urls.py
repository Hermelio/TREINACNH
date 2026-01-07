"""
URL Configuration for core app.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('sobre/', views.about_view, name='about'),
    path('contato/', views.contact_view, name='contact'),
    path('faq/', views.faq_view, name='faq'),
    path('noticias/', views.news_list_view, name='news_list'),
    path('noticias/<slug:slug>/', views.news_detail_view, name='news_detail'),
    path('healthcheck/', views.healthcheck_view, name='healthcheck'),
    path('pagina/<slug:slug>/', views.static_page_view, name='static_page'),
]
