#!/usr/bin/env python3
"""
Debug payment creation issue
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dpramp_project.settings')
django.setup()

from django.test import Client
from notes.models import Product

def debug_payment():
    """Debug payment creation"""
    print("🔍 Debugging Payment Creation...")
    
    # Get a test product
    product = Product.objects.first()
    if not product:
        print("❌ No products found!")
        return
    
    print(f"📦 Test Product: {product.title} (ID: {product.id})")
    print(f"💰 Price: ₹{product.price}")
    
    # Create test client
    client = Client()
    
    # Test order creation
    try:
        response = client.post('/order/create/', {
            'user_name': 'Test User',
            'user_email': 'test@example.com',
            'user_phone': '1234567890'
        })
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Content: {response.content.decode()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Order created successfully!")
                print(f"🔑 Razorpay Order ID: {data.get('razorpay_order_id')}")
            else:
                print(f"❌ Order creation failed: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def main():
    debug_payment()

if __name__ == "__main__":
    main()
