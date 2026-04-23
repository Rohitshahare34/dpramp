# Razorpay Setup Guide - Collect Money for DPRAMP

## Step 1: Create Razorpay Account

1. **Sign Up**: Go to https://razorpay.com/ and create an account
2. **Email Verification**: Verify your email address
3. **Phone Verification**: Verify your phone number

## Step 2: Complete KYC (Know Your Customer)

### Required Documents:
- **PAN Card** (mandatory)
- **Aadhaar Card** (recommended)
- **Bank Account** (for receiving payments)
- **Business Details** (if registered business)

### KYC Process:
1. Login to Razorpay Dashboard
2. Go to "Account & Settings" > "KYC"
3. Upload required documents
4. Fill in business/personal details
5. Wait for verification (usually 1-2 business days)

## Step 3: Add Bank Account for Payouts

1. Go to "Account & Settings" > "Bank Accounts"
2. Add your bank account details:
   - Account Holder Name
   - Account Number
   - IFSC Code
   - Bank Name
3. Verify bank account (small amount will be credited)

## Step 4: Get API Keys

1. Go to "Account & Settings" > "API Keys"
2. You'll see two sets of keys:
   - **Test Keys** (for development)
   - **Live Keys** (for real payments)

3. Copy your keys:
   ```
   Test Key ID: rzp_test_XXXXXXXXXXXXXXXX
   Test Key Secret: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

## Step 5: Update Configuration

1. Open `dpramp_project/razorpay_config.py`
2. Replace placeholder values with your actual keys:

```python
# Test Mode (for development)
RAZORPAY_TEST_KEY_ID = "rzp_test_YOUR_ACTUAL_TEST_KEY_ID"
RAZORPAY_TEST_KEY_SECRET = "YOUR_ACTUAL_TEST_KEY_SECRET"

# Live Mode (for production)
RAZORPAY_LIVE_KEY_ID = "rzp_live_YOUR_ACTUAL_LIVE_KEY_ID"
RAZORPAY_LIVE_KEY_SECRET = "YOUR_ACTUAL_LIVE_KEY_SECRET"

# Account Details
ACCOUNT_HOLDER_NAME = "Your Full Name"
ACCOUNT_NUMBER = "Your Bank Account Number"
IFSC_CODE = "Your Bank IFSC Code"
BANK_NAME = "Your Bank Name"

# Contact Information
CONTACT_EMAIL = "your-email@example.com"
CONTACT_PHONE = "+91XXXXXXXXXX"
```

## Step 6: Test Payment System

1. Start your Django server: `python manage.py runserver`
2. Go to any product page
3. Try making a test purchase
4. Use test card details:
   - Card Number: 4111 1111 1111 1111
   - Expiry: Any future date
   - CVV: Any 3 digits
   - OTP: 123456

## Step 7: Go Live (When Ready)

1. Once testing is complete:
   - Set `DEBUG = False` in settings.py
   - This will switch to live keys
   - Real payments will be processed

## Step 8: Monitor Payouts

1. Login to Razorpay Dashboard
2. Go to "Payouts" section
3. Settle payments to your bank account
4. Monitor transaction history

## Important Notes:

### Security:
- Never commit API keys to Git/GitHub
- Keep your keys secret and secure
- Use environment variables for production

### Fees:
- Razorpay charges 2% per transaction
- + GST (18%) on fees
- + payment gateway charges

### Settlement:
- Payments are settled to your bank account
- Settlement time: T+2 working days
- Minimum settlement amount: Rs. 200

### Support:
- Razorpay Support: support@razorpay.com
- Phone: 1800-123-0022
- Available 24/7

## Troubleshooting:

### Common Issues:
1. **Payment Failed**: Check API keys and network
2. **KYC Pending**: Complete verification
3. **Bank Account Not Added**: Add bank details
4. **Test vs Live**: Ensure correct mode

### Error Messages:
- "Invalid API Key": Check key format
- "Account Not Verified": Complete KYC
- "Payment Gateway Error": Try again later

## Contact Support:
If you need help with setup, contact:
- Razorpay Support: support@razorpay.com
- Django/Razorpay integration: Check documentation

---

**Next Steps:**
1. Create Razorpay account
2. Complete KYC verification
3. Add bank account
4. Get API keys
5. Update configuration file
6. Test payments
7. Go live and start collecting money!
