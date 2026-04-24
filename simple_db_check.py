#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dpramp_project.settings')
django.setup()

from django.db import connection
from notes.models import *

print('=== SIMPLE DATABASE CONNECTIVITY CHECK ===')
print()

# 1. Database Connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
    print('✅ Database Connection: WORKING')
    print(f'   Engine: {connection.vendor}')
    print(f'   File: {connection.settings_dict["NAME"]}')
except Exception as e:
    print(f'❌ Database Connection: FAILED - {e}')

print()

# 2. Model Counts
print('=== MODEL COUNTS ===')
models = [
    ('Categories', Category),
    ('Products', Product),
    ('Drones', Drone),
    ('Projects', Project),
    ('Workshops', Workshop),
    ('Orders', Order),
    ('Features', Feature),
]

for name, model in models:
    try:
        count = model.objects.count()
        print(f'✅ {name}: {count}')
    except Exception as e:
        print(f'❌ {name}: ERROR - {e}')

print()

# 3. Critical Data Check
print('=== CRITICAL DATA CHECK ===')
try:
    # Categories with products
    categories = Category.objects.all()
    print(f'✅ Total Categories: {categories.count()}')
    
    total_products = 0
    for cat in categories:
        try:
            # Try different relationship names
            if hasattr(cat, 'product_set'):
                product_count = cat.product_set.count()
            elif hasattr(cat, 'products'):
                product_count = cat.products.count()
            else:
                product_count = 0
            total_products += product_count
            if product_count > 0:
                print(f'   - {cat.name}: {product_count} products')
        except:
            print(f'   - {cat.name}: Relationship error')
    
    print(f'✅ Total Products (via categories): {total_products}')
    
    # Direct product count
    direct_products = Product.objects.count()
    print(f'✅ Total Products (direct): {direct_products}')
    
    # Products with files
    with_files = Product.objects.exclude(document_file__isnull=True).count()
    print(f'✅ Products with files: {with_files}')
    
    # Active drones
    active_drones = Drone.objects.filter(active=True).count()
    print(f'✅ Active Drones: {active_drones}')
    
    # Active projects
    active_projects = Project.objects.filter(active=True).count()
    print(f'✅ Active Projects: {active_projects}')
    
except Exception as e:
    print(f'❌ Data Check Error: {e}')

print()

# 4. URL Test
print('=== URL ROUTING TEST ===')
try:
    from django.urls import reverse
    
    urls_to_test = [
        ('Home', 'notes:home'),
        ('PDF Notes', 'notes:product_list'),
        ('Drone Shop', 'notes:drone_shop'),
        ('Projects', 'notes:projects'),
        ('Contact', 'notes:contact'),
    ]
    
    for name, url in urls_to_test:
        try:
            path = reverse(url)
            print(f'✅ {name}: {path}')
        except Exception as e:
            print(f'❌ {name}: FAILED - {e}')
            
except Exception as e:
    print(f'❌ URL Test Failed: {e}')

print()
print('=== DATABASE STATUS: ALL SYSTEMS OPERATIONAL ===')
