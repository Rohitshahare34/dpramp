# DPRAMP-TECH SOLUTIONS - Django PDF Selling Platform

This project converts the existing Finanza static website template into a fully functional Django application with PDF selling capabilities while preserving the original UI completely.

## Features

- **Preserved Original UI**: All existing pages and styling maintained exactly
- **PDF Selling System**: Upload, manage, and sell PDF notes securely
- **Category-based Organization**: Organize PDFs by categories
- **Secure Payment Integration**: Razorpay payment gateway integration
- **Token-based Downloads**: 10-minute expiry secure download links
- **Auto-download**: Automatic PDF download after successful payment
- **Admin Panel**: Full Django admin for managing products and orders
- **Responsive Design**: Mobile-friendly responsive layout

## Project Structure

```
dpramp application/
|
|-- dpramp/                 # Django project settings
|   |-- __init__.py
|   |-- settings.py
|   |-- urls.py
|   |-- wsgi.py
|   |-- asgi.py
|
|-- notes/                  # Django app
|   |-- models.py           # Database models
|   |-- views.py            # View functions
|   |-- urls.py             # App URLs
|   |-- admin.py            # Admin configuration
|   |-- apps.py
|   |-- management/
|       |-- commands/
|           |-- setup_sample_data.py
|
|-- templates/              # Django templates
|   |-- base.html           # Base template
|   |-- index.html          # Homepage
|   |-- about.html
|   |-- contact.html
|   |-- service.html
|   |-- project.html
|   |-- feature.html
|   |-- team.html
|   |-- testimonial.html
|   |-- products/
|       |-- product_list.html
|       |-- product_detail.html
|       |-- payment_success.html
|       |-- download_error.html
|
|-- DPRAMP/                # Original static files
|   |-- css/
|   |-- js/
|   |-- img/
|   |-- lib/
|   |-- scss/
|
|-- manage.py
|-- requirements.txt
|-- README.md
```

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit `dpramp/settings.py` and update the following:

```python
# Razorpay Configuration
RAZORPAY_KEY_ID = 'your-razorpay-key-id'
RAZORPAY_KEY_SECRET = 'your-razorpay-key-secret'

# Update SECRET_KEY for production
SECRET_KEY = 'your-secure-secret-key-here'
```

### 3. Database Setup

```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### 4. Setup Sample Data (Optional)

```bash
# Create sample categories and products
python manage.py setup_sample_data
```

### 5. Collect Static Files

```bash
python manage.py collectstatic
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to access the application.

## Admin Panel

Access the Django admin panel at `http://127.0.0.1:8000/admin/`

### Admin Features:
- **Categories**: Add and manage PDF categories
- **Products**: Upload PDFs, set prices, manage preview images
- **Orders**: View and manage customer orders
- **Download Tokens**: Monitor download links and expiry

## Key Features Implementation

### 1. PDF Product Management
- Admin can upload PDF files with thumbnails
- Support for multiple preview images (3-4 pages)
- Category-based organization
- Price management

### 2. Payment System
- Razorpay integration for secure payments
- Real-time payment verification
- Order management system

### 3. Secure Download System
- Token-based download links
- 10-minute expiry for security
- Automatic download after payment
- Error handling for expired/invalid links

### 4. UI Preservation
- All original HTML pages converted to Django templates
- Static paths converted to Django template tags
- Original styling and animations maintained
- Responsive design preserved

## URL Structure

### Static Pages:
- `/` - Homepage (with featured products)
- `/about/` - About page
- `/services/` - Services page (with featured products)
- `/contact/` - Contact page
- `/projects/` - Projects page
- `/features/` - Features page
- `/team/` - Team page
- `/testimonial/` - Testimonials page

### Product Pages:
- `/pdf-notes/` - Product listing page (category-wise)
- `/pdf-notes/<slug>/` - Product detail page

### Payment & Download:
- `/create-order/<product_id>/` - Create payment order
- `/payment-callback/` - Razorpay payment callback
- `/payment-success/<order_id>/` - Payment success page
- `/download/<token>/` - Secure PDF download

## Security Features

- CSRF protection on all forms
- Token-based download verification
- Payment signature verification
- Expired token handling
- Direct media URL protection
- SQL injection prevention through Django ORM

## Production Deployment

### 1. Environment Setup
- Set `DEBUG = False` in settings
- Configure `ALLOWED_HOSTS`
- Use environment variables for sensitive data

### 2. Static Files
- Configure static file serving (Nginx/Apache)
- Run `collectstatic` command

### 3. Database
- Use PostgreSQL/MySQL for production
- Configure database settings

### 4. Security
- Enable HTTPS
- Configure secure headers
- Set up proper file permissions

## Support

For any issues or questions:
- Check the Django admin for error logs
- Verify Razorpay credentials
- Ensure static files are properly configured
- Check media file permissions

## License

This project maintains the original Creative Commons Attribution 4.0 International License from the Finanza template.
