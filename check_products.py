#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dpramp_project.settings')
django.setup()

from notes.models import Category, Product

print('=== Product Database Check ===')
print(f'Total categories: {Category.objects.count()}')
print(f'Total products: {Product.objects.count()}')

print('\n=== All Categories ===')
for category in Category.objects.all():
    print(f'- {category.name} (slug: {category.slug})')
    products = category.product_set.all()
    print(f'  Products: {products.count()}')
    for product in products[:3]:  # Show first 3 products per category
        print(f'    - {product.title} (active: {product.document_file is not None})')

print('\n=== All Products ===')
for product in Product.objects.all():
    print(f'- {product.title}')
    print(f'  Category: {product.category.name if product.category else "No category"}')
    print(f'  Price: {product.price}')
    print(f'  Has document: {product.document_file is not None}')
    print(f'  Has thumbnail: {product.thumbnail is not None}')
    print(f'  Slug: {product.slug}')
    print()
