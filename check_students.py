#!/usr/bin/env python
"""
Script para verificar alunos em uma cidade
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import StudentLead, State

# Verificar Mongaguá
sp = State.objects.get(code='SP')
students = StudentLead.objects.filter(state=sp, city__iexact='Mongagua')

print(f'Total de alunos em Mongaguá/SP: {students.count()}')
print('\nPrimeiros 10 alunos:')
for i, student in enumerate(students[:10], 1):
    print(f'{i}. {student.name} | {student.phone} | Categoria {student.category}')

# Verificar São Paulo
students_sp = StudentLead.objects.filter(state=sp, city__iexact='Sao Paulo')
print(f'\nTotal de alunos em São Paulo/SP: {students_sp.count()}')

# Ver todas as cidades distintas em SP
from django.db.models import Count
cities = StudentLead.objects.filter(state__code='SP').values('city').annotate(total=Count('id')).order_by('-total')[:10]
print('\nTop 10 cidades com mais alunos em SP:')
for city in cities:
    print(f"  {city['city']}: {city['total']} alunos")
