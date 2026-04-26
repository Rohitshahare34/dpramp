#!/usr/bin/env python3
"""
Test Payment Fix for DPRAMP
Run this to test Razorpay integration
"""

import os
import django
import razorpay

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dpramp_project.settings')
django.setup()

from django.conf import settings
from notes.models import Order

def test_razorpay_connection():
    """Test Razorpay API connection"""
    print("🔍 Testing Razorpay Connection...")
    
    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Test by creating a small order
        order_data = {
            'amount': 100,  # ₹1
            'currency': 'INR',
            'receipt': 'test_receipt_001',
            'payment_capture': 1
        }
        
        order = client.order.create(order_data)
        print(f"✅ Razorpay Connection Successful!")
        print(f"📝 Test Order ID: {order['id']}")
        print(f"💰 Amount: ₹{order['amount']/100}")
        
        return True
        
    except Exception as e:
        print(f"❌ Razorpay Connection Failed: {str(e)}")
        return False

def check_pending_orders():
    """Check for pending orders"""
    print("\n🔍 Checking Pending Orders...")
    
    pending_orders = Order.objects.filter(payment_status='pending')
    
    if pending_orders.exists():
        print(f"📊 Found {pending_orders.count()} pending orders:")
        for order in pending_orders:
            print(f"  - Order {order.order_id}: ₹{order.amount} ({order.order_type})")
            print(f"    Razorpay Order ID: {order.razorpay_order_id}")
            print(f"    Created: {order.created_at}")
            print()
    else:
        print("✅ No pending orders found")

def main():
    print("🚀 DPRAMP Payment Test Tool")
    print("=" * 40)
    
    # Test Razorpay connection
    if test_razorpay_connection():
        print("\n✅ Razorpay is working correctly!")
        
        # Check pending orders
        check_pending_orders()
        
        print("\n💡 Next Steps:")
        print("1. Use test card: 4111 1111 1111 1111")
        print("2. Any future expiry date")
        print("3. Any 3-digit CVV")
        print("4. Complete payment flow")
        
    else:
        print("\n❌ Fix Razorpay keys first!")

if __name__ == "__main__":
    main()
