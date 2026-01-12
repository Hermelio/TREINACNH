#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SHOW TABLES")
tables = [t[0] for t in cursor.fetchall()]

print("All tables:")
for table in sorted(tables):
    print(f"  - {table}")

if 'marketplace_studentlead_categories' in tables:
    print("\n✓ ManyToMany table exists!")
else:
    print("\n✗ ManyToMany table NOT found. Creating...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marketplace_studentlead_categories (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            studentlead_id BIGINT NOT NULL,
            categorycnh_id BIGINT NOT NULL,
            UNIQUE KEY (studentlead_id, categorycnh_id),
            FOREIGN KEY (studentlead_id) REFERENCES marketplace_studentlead(id),
            FOREIGN KEY (categorycnh_id) REFERENCES marketplace_categorycnh(id)
        )
    """)
    print("✓ Table created!")
