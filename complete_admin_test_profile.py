#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from marketplace.models import InstructorProfile, CategoryCNH, City

# Pegar admin_test
user = User.objects.get(username='admin_test')
instructor = InstructorProfile.objects.get(user=user)

print(f"Atualizando perfil de {user.username}...")

# Pegar cidade (São Paulo como exemplo)
city = City.objects.filter(name__icontains='São Paulo').first()
if not city:
    city = City.objects.first()

# Atualizar dados completos
instructor.city = city
instructor.bio = "Instrutor experiente com mais de 10 anos ensinando direção defensiva. Metodologia prática e personalizada para cada aluno."
instructor.neighborhoods_text = "Centro, Jardins, Vila Mariana"
instructor.gender = 'M'
instructor.age = 35
instructor.years_experience = 10
instructor.has_own_car = True
instructor.car_model = "Volkswagen Gol 2022"
instructor.available_morning = True
instructor.available_afternoon = True
instructor.available_evening = False
instructor.base_price_per_hour = 80.00
instructor.price_notes = "Pacotes com desconto disponíveis"
instructor.is_visible = True
instructor.save()

# Adicionar categorias B e C
cat_b = CategoryCNH.objects.filter(code='B').first()
cat_c = CategoryCNH.objects.filter(code='C').first()

if cat_b:
    instructor.categories.add(cat_b)
if cat_c:
    instructor.categories.add(cat_c)

print("✅ Perfil do admin_test completado com sucesso!")
print(f"   Cidade: {instructor.city}")
print(f"   Bio: {instructor.bio[:50]}...")
print(f"   Categorias: {', '.join([c.code for c in instructor.categories.all()])}")
print(f"   Visível: {instructor.is_visible}")
