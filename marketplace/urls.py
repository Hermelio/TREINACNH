"""
URL Configuration for marketplace app.
"""
from django.urls import path
from . import views
from .views_map import instructors_map_view
from .api_views import get_cities_by_state

app_name = 'marketplace'

urlpatterns = [
    # API endpoints (must come first)
    path('api/cidades/<str:state_code>/', get_cities_by_state, name='api_cities_by_state'),
    
    # Instructor management (authenticated) - must come before dynamic routes
    path('meu-perfil/editar/', views.instructor_profile_edit_view, name='instructor_profile_edit'),
    path('meus-leads/', views.my_leads_view, name='my_leads'),
    path('lead/<int:lead_pk>/atualizar/', views.lead_update_status_view, name='lead_update_status'),
    
    # Public pages
    path('', instructors_map_view, name='instructors_map'),
    path('cidades/', views.cities_list_view, name='cities_list'),
    path('instrutor/<int:pk>/', views.instructor_detail_view, name='instructor_detail'),
    path('instrutor/<int:instructor_pk>/solicitar-contato/', views.lead_create_view, name='lead_create'),
    
    # Dynamic routes (must come last to avoid conflicts)
    path('<str:state_code>/<slug:city_slug>/', views.city_instructors_list_view, name='city_list'),
]
