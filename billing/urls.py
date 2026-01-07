"""
URL Configuration for billing app.
"""
from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.plans_view, name='plans'),
    path('minha-assinatura/', views.my_subscription_view, name='my_subscription'),
]
