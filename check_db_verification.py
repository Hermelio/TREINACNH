#!/usr/bin/env python
"""
Script to check ACTUAL database values for is_verified field
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import InstructorProfile

# Get ALL instructors and show ACTUAL database values
instructors = InstructorProfile.objects.all().order_by('id')

print("=" * 100)
print("VALORES REAIS DO BANCO DE DADOS - Campo 'is_verified'")
print("=" * 100)

verified_count = 0
not_verified_count = 0

for inst in instructors:
    status_symbol = "✓" if inst.is_verified else "✗"
    status_text = "VERIFICADO (is_verified=True)" if inst.is_verified else "NÃO VERIFICADO (is_verified=False)"
    
    if inst.is_verified:
        verified_count += 1
    else:
        not_verified_count += 1
    
    print(f"{status_symbol} ID {inst.id:3d}: {inst.user.get_full_name():40s} - {status_text}")

print("\n" + "=" * 100)
print(f"RESUMO REAL DO BANCO DE DADOS:")
print(f"  Total de instrutores: {instructors.count()}")
print(f"  is_verified=True:  {verified_count}")
print(f"  is_verified=False: {not_verified_count}")
print("=" * 100)

# Show SQL query to confirm
print("\nConfirmação via SQL direto:")
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT 
            is_verified,
            COUNT(*) as total
        FROM marketplace_instructorprofile
        GROUP BY is_verified
        ORDER BY is_verified
    """)
    rows = cursor.fetchall()
    print("is_verified | total")
    print("------------|------")
    for row in rows:
        verified_text = "True " if row[0] else "False"
        print(f"{verified_text:11s} | {row[1]:5d}")
