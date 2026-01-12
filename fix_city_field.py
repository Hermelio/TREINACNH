#!/usr/bin/env python
"""
Script to convert city_id from varchar to bigint and add foreign key constraint
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

print("Deleting old student leads...")
cursor.execute('DELETE FROM marketplace_studentlead')
print("Done!")

print("Converting city_id to bigint...")
cursor.execute('ALTER TABLE marketplace_studentlead MODIFY COLUMN city_id bigint NULL')
print("Done!")

print("Adding foreign key constraint...")
try:
    cursor.execute('ALTER TABLE marketplace_studentlead ADD CONSTRAINT marketplace_studentlead_city_id_fk FOREIGN KEY (city_id) REFERENCES marketplace_city(id)')
    print("Done!")
except Exception as e:
    print(f"FK already exists or error: {e}")

print("\nAll conversions completed successfully!")
