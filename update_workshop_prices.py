#!/usr/bin/env python3
"""
Update workshop prices to ₹100
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dpramp_project.settings')
django.setup()

from notes.models import Workshop

def update_workshop_prices():
    """Update all workshop prices to ₹100"""
    print("🔧 Updating Workshop Prices to ₹100")
    print("=" * 40)
    
    workshops = Workshop.objects.all()
    count = workshops.count()
    
    if count > 0:
        print(f"📊 Found {count} workshops:")
        
        for workshop in workshops:
            old_price = workshop.entry_fee
            workshop.entry_fee = 100.00
            workshop.save()
            print(f"  ✅ {workshop.title}: ₹{old_price} → ₹100")
        
        print(f"\n✅ Updated {count} workshop prices to ₹100!")
    else:
        print("❌ No workshops found in database")

def check_workshop_prices():
    """Check all workshop prices"""
    print("\n📊 Current Workshop Prices:")
    print("=" * 30)
    
    workshops = Workshop.objects.all()
    for workshop in workshops:
        print(f"  - {workshop.title}: ₹{workshop.entry_fee}")
        print(f"    Date: {workshop.date}")
        print(f"    Location: {workshop.location}")

def main():
    update_workshop_prices()
    check_workshop_prices()
    
    print("\n🚀 All Payment Types Ready:")
    print("1. 🚁 Drones: ₹100 each")
    print("2. 📚 Study Materials: ₹1 each") 
    print("3. 🎓 Workshops: ₹100 each")
    print("4. 💳 All payments via Razorpay")
    print("5. 🧪 Test with card: 4111 1111 1111 1111")

if __name__ == "__main__":
    main()
