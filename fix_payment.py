#!/usr/bin/env python3
"""
Quick Payment Fix for DPRAMP
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dpramp_project.settings')
django.setup()

from notes.models import Order

def clear_pending_orders():
    """Clear all pending orders"""
    pending = Order.objects.filter(payment_status='pending')
    count = pending.count()
    
    if count > 0:
        print(f"🗑️  Clearing {count} pending orders...")
        pending.delete()
        print("✅ Pending orders cleared!")
    else:
        print("✅ No pending orders to clear")

def main():
    print("🔧 DPRAMP Payment Fix Tool")
    print("=" * 30)
    
    clear_pending_orders()
    
    print("\n💡 Payment Instructions:")
    print("1. Use TEST card: 4111 1111 1111 1111")
    print("2. Expiry: 12/25 (or any future date)")
    print("3. CVV: 123 (or any 3 digits)")
    print("4. Name: Test User")
    print("5. Click 'Pay' and complete the flow")
    
    print("\n⚠️  Important:")
    print("- These are TEST keys - no real money will be deducted")
    print("- Only test cards will work with test keys")
    print("- Real cards will fail in test mode")

if __name__ == "__main__":
    main()
