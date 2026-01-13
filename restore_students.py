"""
Script para restaurar alunos do StudentLead.csv para o banco de dados
"""
import os
import django
import csv
import json
from datetime import datetime
from django.utils.dateparse import parse_datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import StudentLead, State, City, CategoryCNH

def restore_students():
    """Restaura alunos do CSV para o banco"""
    
    # Limpar tabela atual (já está vazia mas por garantia)
    StudentLead.objects.all().delete()
    
    count = 0
    errors = []
    
    with open('StudentLead.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                # Parse metadata JSON
                metadata = {}
                try:
                    if row.get('metadata'):
                        metadata = json.loads(row['metadata'])
                except:
                    pass
                
                # Buscar ou criar estado
                state = None
                if row.get('state'):
                    state, _ = State.objects.get_or_create(
                        code=row['state'],
                        defaults={'name': row['state']}
                    )
                
                # Buscar ou criar cidade
                city = None
                if row.get('city') and state:
                    city, _ = City.objects.get_or_create(
                        name=row['city'],
                        state=state
                    )
                
                # Extrair email do metadata
                email = metadata.get('email', '') or ''
                
                # Parse dates
                created_at = parse_datetime(row.get('createdAt', '')) or datetime.now()
                updated_at = parse_datetime(row.get('updatedAt', '')) or datetime.now()
                contacted_at = parse_datetime(row.get('contactedAt', '')) if row.get('contactedAt') else None
                
                # Criar aluno
                student = StudentLead.objects.create(
                    external_id=row.get('id', ''),
                    name=row.get('name', ''),
                    email=email,
                    phone=row.get('phone', ''),
                    state=state,
                    city=city,
                    has_theory=metadata.get('hasTheory', False),
                    accept_whatsapp=row.get('acceptWhatsApp', 'false').lower() == 'true',
                    accept_email=row.get('acceptMarketing', 'false').lower() == 'true',
                    accept_terms=row.get('acceptTerms', 'false').lower() == 'true',
                    is_contacted=row.get('isContacted', 'false').lower() == 'true',
                    contacted_at=contacted_at,
                    metadata=metadata,
                    notes=row.get('notes', ''),
                    created_at=created_at,
                    updated_at=updated_at
                )
                
                # Adicionar categorias
                category_str = row.get('category', 'B')
                for cat_code in category_str:
                    if cat_code in ['A', 'B', 'C', 'D', 'E']:
                        cat, _ = CategoryCNH.objects.get_or_create(
                            code=cat_code,
                            defaults={'label': f'Categoria {cat_code}'}
                        )
                        student.categories.add(cat)
                
                count += 1
                
                if count % 50 == 0:
                    print(f"✓ {count} alunos restaurados...")
                    
            except Exception as e:
                errors.append(f"Linha {count + 1} ({row.get('name', 'N/A')}): {str(e)}")
    
    print(f"\n✅ Restauração concluída!")
    print(f"📊 Total: {count} alunos")
    
    if errors:
        print(f"\n⚠️  {len(errors)} erros:")
        for error in errors[:10]:  # Mostrar só os 10 primeiros
            print(f"  - {error}")
    
    # Verificar total no banco
    total = StudentLead.objects.count()
    print(f"\n✓ Verificação: {total} alunos no banco de dados")
    
    # Estatísticas por estado
    from django.db.models import Count
    stats = StudentLead.objects.values('state__code').annotate(total=Count('id')).order_by('-total')
    print(f"\n📍 Alunos por estado:")
    for stat in stats[:10]:
        print(f"  {stat['state__code']}: {stat['total']} alunos")

if __name__ == '__main__':
    restore_students()
