#!/usr/bin/env python
"""Detalha por que alguns contatos nao receberao o email."""
import os, sys, django
sys.path.insert(0, '/var/www/TREINACNH')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from django.contrib.auth.models import User
from marketplace.models import StudentLead

# --- StudentLead (leads do CSV) ---
total_leads = StudentLead.objects.count()
sem_email   = StudentLead.objects.filter(email='').count()
nao_aceita  = StudentLead.objects.exclude(email='').filter(accept_email=False).count()
aceita      = StudentLead.objects.exclude(email='').filter(accept_email=True).count()

existing = set(User.objects.exclude(email='').values_list('email', flat=True))
leads_accept = StudentLead.objects.exclude(email='').filter(accept_email=True)
ja_tem_conta = sum(1 for l in leads_accept if l.email.lower() in {e.lower() for e in existing})
leads_enviados = aceita - ja_tem_conta

print('=== StudentLead (importados do CSV) ===')
print(f'  Total de leads:                      {total_leads}')
print(f'  Sem email cadastrado:                {sem_email}')
print(f'  Nao aceitam email (accept_email=F):  {nao_aceita}')
print(f'  Aceitam mas ja tem conta Django:     {ja_tem_conta}')
print(f'  >>> Serao enviados:                  {leads_enviados}')

# --- Usuarios Django ---
total_users = User.objects.count()
inativos    = User.objects.filter(is_active=False).count()
sem_email_u = User.objects.filter(email='').count()
users_enviados = total_users - inativos - sem_email_u

print()
print('=== Usuarios Django (cadastrados no portal) ===')
print(f'  Total de usuarios:                   {total_users}')
print(f'  Inativos (is_active=False):          {inativos}')
print(f'  Sem email:                           {sem_email_u}')
print(f'  >>> Serao enviados:                  {users_enviados}')

print()
print(f'TOTAL GERAL: {leads_enviados + users_enviados}')
