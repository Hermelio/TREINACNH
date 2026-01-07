"""
URL Configuration for verification app.
"""
from django.urls import path
from . import views

app_name = 'verification'

urlpatterns = [
    path('documentos/enviar/', views.document_upload_view, name='document_upload'),
    path('documentos/', views.my_documents_view, name='my_documents'),
]
