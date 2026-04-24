#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dpramp_project.settings')
django.setup()

from django.db import connection
from notes.models import *

print('=== DATABASE CONNECTIVITY CHECK ===')
print()

# 1. Test Database Connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
    print('✅ Database Connection: OK')
    print(f'   Database Engine: {connection.vendor}')
    print(f'   Database Name: {connection.settings_dict["NAME"]}')
except Exception as e:
    print(f'❌ Database Connection: FAILED - {e}')
    exit(1)

print()

# 2. Check All Models
print('=== MODEL CONNECTIVITY CHECK ===')
models_to_check = [
    ('Category', Category),
    ('Product', Product),
    ('Order', Order),
    ('DownloadToken', DownloadToken),
    ('Contact', Contact),
    ('Project', Project),
    ('Workshop', Workshop),
    ('WorkshopRegistration', WorkshopRegistration),
    ('Feature', Feature),
    ('Drone', Drone),
    ('CustomerSupport', CustomerSupport),
    ('WebsitePopup', WebsitePopup),
]

for model_name, model_class in models_to_check:
    try:
        count = model_class.objects.count()
        print(f'✅ {model_name}: {count} records')
    except Exception as e:
        print(f'❌ {model_name}: FAILED - {e}')

print()

# 3. Check Critical Relationships
print('=== RELATIONSHIP CHECK ===')
try:
    # Category-Product Relationship
    categories_with_products = Category.objects.filter(product_set__isnull=False).distinct().count()
    print(f'✅ Categories with products: {categories_with_products}/{Category.objects.count()}')
    
    # Product-Category Relationship
    products_with_category = Product.objects.filter(category__isnull=False).count()
    print(f'✅ Products with categories: {products_with_category}/{Product.objects.count()}')
    
    # Product-Order Relationship
    products_with_orders = Product.objects.filter(orders__isnull=False).distinct().count()
    print(f'✅ Products with orders: {products_with_orders}')
    
    # Active Products
    active_products = Product.objects.filter(document_file__isnull=False).count()
    print(f'✅ Products with files: {active_products}/{Product.objects.count()}')
    
except Exception as e:
    print(f'❌ Relationship Check: FAILED - {e}')

print()

# 4. Check Sample Data
print('=== SAMPLE DATA VERIFICATION ===')
try:
    # Check if essential data exists
    if Category.objects.exists():
        print('✅ Categories exist')
        for cat in Category.objects.all()[:3]:
            print(f'   - {cat.name}')
    else:
        print('⚠️  No categories found')
    
    if Product.objects.exists():
        print('✅ Products exist')
        for prod in Product.objects.all()[:3]:
            print(f'   - {prod.title} (₹{prod.price})')
    else:
        print('⚠️  No products found')
    
    if Drone.objects.exists():
        print('✅ Drones exist')
        for drone in Drone.objects.all()[:2]:
            print(f'   - {drone.name} (₹{drone.price})')
    else:
        print('⚠️  No drones found')
        
    if Project.objects.exists():
        print('✅ Projects exist')
        for proj in Project.objects.all()[:2]:
            print(f'   - {proj.title}')
    else:
        print('⚠️  No projects found')
        
except Exception as e:
    print(f'❌ Sample Data Check: FAILED - {e}')

print()

# 5. Check URL Routing
print('=== URL ROUTING CHECK ===')
try:
    from django.urls import reverse
    from notes import urls as notes_urls
    
    # Test key URLs
    key_urls = [
        ('home', 'notes:home'),
        ('product_list', 'notes:product_list'),
        ('drone_shop', 'notes:drone_shop'),
        ('projects', 'notes:projects'),
        ('contact', 'notes:contact'),
    ]
    
    for name, url_name in key_urls:
        try:
            url = reverse(url_name)
            print(f'✅ {name}: {url}')
        except Exception as e:
            print(f'❌ {name}: FAILED - {e}')
            
except Exception as e:
    print(f'❌ URL Routing Check: FAILED - {e}')

print()
print('=== DATABASE CHECK COMPLETE ===')
