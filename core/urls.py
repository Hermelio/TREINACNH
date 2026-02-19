"""
URL Configuration for core app.
"""
from django.urls import path
from . import views
from django.contrib.sitemaps.views import sitemap
from .sitemap import sitemaps

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
    path('alunos/<str:state_code>/<str:city_name>/', views.city_students_view, name='city_students'),
    path('lcp-test/', views.lcp_test_view, name='lcp_test'),
    path('mobile-lcp-test/', views.mobile_lcp_test_view, name='mobile_lcp_test'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('google8a3de9cf5898f665.html', views.google_site_verification, name='google_site_verification'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
