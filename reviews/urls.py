"""
URL Configuration for reviews app.
"""
from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('instrutor/<int:instructor_pk>/avaliar/', views.review_create_view, name='review_create'),
    path('instrutor/<int:instructor_pk>/denunciar/', views.report_create_view, name='report_create'),
]
