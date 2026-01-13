"""
URL Configuration for billing app.
"""
from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.plans_view, name='plans'),
    path('minha-assinatura/', views.my_subscription_view, name='my_subscription'),
    path('checkout/<int:subscription_id>/', views.checkout_view, name='checkout'),
    path('pagamento/sucesso/', views.payment_success_view, name='payment_success'),
    path('pagamento/falha/', views.payment_failure_view, name='payment_failure'),
    path('pagamento/pendente/', views.payment_pending_view, name='payment_pending'),
