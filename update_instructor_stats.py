#!/usr/bin/env python
"""
Atualizar estatísticas de todos os instrutores (média de avaliações e total de alunos).
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/var/www/TREINACNH')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile

# Buscar todos os instrutores
instructors = InstructorProfile.objects.all()

print(f'📊 Atualizando estatísticas de {instructors.count()} instrutores...\n')

for instructor in instructors:
    print(f'👤 {instructor.user.get_full_name()}')
    print(f'   Antes: {instructor.total_students} alunos, {instructor.total_reviews} avaliações, média: {instructor.average_rating}')
    
    instructor.update_statistics()
    instructor.refresh_from_db()
    
    print(f'   Depois: {instructor.total_students} alunos, {instructor.total_reviews} avaliações, média: {instructor.average_rating}')
    print()

print(f'✅ Estatísticas atualizadas com sucesso!')
