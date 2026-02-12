"""
Script to populate missing cities from StudentLeadatual.csv
"""
import os
import sys
import django
import csv

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import City, State

def populate_missing_cities():
    """Read CSV and create missing cities"""
    csv_file = 'StudentLeadatual.csv'
    
    created_count = 0
    skipped_count = 0
    error_count = 0
    
    print("Reading CSV and checking for missing cities...")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Collect unique city/state combinations
        city_state_pairs = set()
        for row in reader:
            city_name = row.get('city', '').strip()
            state_code = row.get('state', '').strip().upper()
            
            if city_name and state_code:
                city_state_pairs.add((city_name, state_code))
        
        print(f"Found {len(city_state_pairs)} unique city/state combinations in CSV")
        
        # Process each combination
        for city_name, state_code in sorted(city_state_pairs):
            try:
                # Get state
                try:
                    state = State.objects.get(code=state_code)
                except State.DoesNotExist:
                    print(f"⚠️  State not found: {state_code}")
                    error_count += 1
                    continue
                
                # Check if city exists
                city = City.objects.filter(name__iexact=city_name, state=state).first()
                
                if city:
                    skipped_count += 1
                else:
                    # Create city
                    City.objects.create(
                        name=city_name,
                        state=state,
                        latitude=0.0,  # Default coordinates
                        longitude=0.0
                    )
                    print(f"✓ Created: {city_name}/{state_code}")
                    created_count += 1
                    
            except Exception as e:
                print(f"❌ Error processing {city_name}/{state_code}: {e}")
                error_count += 1
    
    print("\n" + "="*60)
    print("Population completed!")
    print(f"Created: {created_count}")
    print(f"Already existed: {skipped_count}")
    print(f"Errors: {error_count}")
    print("="*60)

if __name__ == '__main__':
    populate_missing_cities()
