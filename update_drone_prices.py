#!/usr/bin/env python3
"""
Update all drone prices to ₹100
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dpramp_project.settings')
django.setup()

from notes.models import Drone, Product, Workshop

def update_drone_prices():
    """Update all drone prices to ₹100"""
    print("🔧 Updating Drone Prices to ₹100")
    print("=" * 40)
    
    drones = Drone.objects.all()
    count = drones.count()
    
    if count > 0:
        print(f"📊 Found {count} drones:")
        
        for drone in drones:
            old_price = drone.price
            drone.price = 100.00
            drone.save()
            print(f"  ✅ {drone.name}: ₹{old_price} → ₹100")
        
        print(f"\n✅ Updated {count} drone prices to ₹100!")
    else:
        print("❌ No drones found in database")

def check_all_prices():
    """Check all product prices"""
    print("\n📊 Current Prices:")
    print("=" * 30)
    
    # Drones
    drones = Drone.objects.all()
    print(f"\n🚁 Drones ({drones.count()}):")
    for drone in drones:
        print(f"  - {drone.name}: ₹{drone.price}")
    
    # Study Materials
    products = Product.objects.all()
    print(f"\n📚 Study Materials ({products.count()}):")
    for product in products:
        print(f"  - {product.title}: ₹{product.price}")
    
    # Workshops
    workshops = Workshop.objects.all()
    print(f"\n🎓 Workshops ({workshops.count()}):")
    for workshop in workshops:
        print(f"  - {workshop.title}: ₹{workshop.entry_fee}")

def main():
    update_drone_prices()
    check_all_prices()
    
    print("\n🚀 Ready for Testing:")
    print("1. All drones now cost ₹100")
    print("2. Use test card: 4111 1111 1111 1111")
    print("3. Test all payment types:")
    print("   - Drone Purchase")
    print("   - Study Materials")
    print("   - Workshop Registration")

if __name__ == "__main__":
    main()
