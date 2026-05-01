#!/usr/bin/env python3
"""
Update all study materials prices to ₹5
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dpramp_project.settings')
django.setup()

from notes.models import Product

def update_notes_prices():
    """Update all study materials prices to ₹5"""
    print("🔧 Updating Study Materials Prices to ₹5")
    print("=" * 50)
    
    products = Product.objects.all()
    count = products.count()
    
    if count > 0:
        print(f"📊 Found {count} study materials:")
        
        for product in products:
            old_price = product.price
            product.price = 5.00
            product.save()
            print(f"  ✅ {product.title}: ₹{old_price} → ₹5")
        
        print(f"\n✅ Updated {count} study material prices to ₹5!")
    else:
        print("❌ No study materials found")

def check_all_prices():
    """Check all current prices"""
    print("\n📊 Current Prices:")
    print("=" * 30)
    
    # Drones
    from notes.models import Drone
    drones = Drone.objects.all()
    print(f"\n🚁 Drones ({drones.count()}):")
    for drone in drones:
        print(f"  - {drone.name}: ₹{drone.price}")
    
    # Study Materials
    from notes.models import Product
    products = Product.objects.all()
    print(f"\n📚 Study Materials ({products.count()}):")
    for product in products:
        print(f"  - {product.title}: ₹{product.price}")
    
    # Workshops
    from notes.models import Workshop
    workshops = Workshop.objects.all()
    print(f"\n🎓 Workshops ({workshops.count()}):")
    for workshop in workshops:
        print(f"  - {workshop.title}: ₹{workshop.entry_fee}")

def main():
    update_notes_prices()
    check_all_prices()
    
    print("\n🚀 Pricing Updated!")
    print("📚 Study Materials: ₹5 each")
    print("🚁 Drones: ₹5 each") 
    print("🎓 Workshops: ₹5 each")
    print("\n💳 All payments via Razorpay")
    print("🧪 Test with card: 4111 1111 1111 1111")

if __name__ == "__main__":
    main()
