from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.files import File
from django.conf import settings
from django.contrib import messages
from decimal import Decimal
from io import BytesIO
import razorpay
import uuid
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from .models import Category, Product, Order, DownloadToken, ProductImage, Contact, Project, Workshop, WorkshopForm, WorkshopRegistration, Feature, Drone, CustomerSupport, WebsitePopup


def home(request):
    """Home page view"""
    featured_notes = Product.objects.all()[:6]  # Get first 6 products as featured
    features = Feature.objects.filter(active=True)  # Get all active features
    # Always show 4 drones on home page (featured first, then latest)
    featured_drones = (
        Drone.objects.filter(active=True)
        .order_by("-featured", "-created_at")
        [:4]
    )
    featured_projects = Project.objects.filter(active=True).order_by('-created_at')[:6]  # Get latest projects
    
    # Get active popup/poster
    active_popup = WebsitePopup.objects.filter(is_active=True).first()
    
    return render(request, "index.html", {
        "featured_notes": featured_notes,
        "features": features,
        "featured_drones": featured_drones,
        "featured_projects": featured_projects,
        "active_popup": active_popup
    })


def drone_list(request):
    """Drone listing page view"""
    drones = Drone.objects.filter(active=True)
    return render(request, "drone_list.html", {"drones": drones})


def drone_detail(request, slug):
    """Drone detail page view"""
    drone = get_object_or_404(Drone, slug=slug, active=True)
    return render(request, "drone_detail.html", {"drone": drone})


@require_http_methods(["POST"])
def create_drone_order(request, slug):
    """Create Razorpay order for drone purchase."""
    drone = get_object_or_404(Drone, slug=slug, active=True)

    user_name = request.POST.get("name", "").strip()
    user_email = request.POST.get("email", "").strip().lower()
    user_phone = request.POST.get("phone", "").strip()
    shipping_address = request.POST.get("shipping_address", "").strip()

    if not user_name or not user_email or not user_phone:
        return JsonResponse({"error": "Name, email and phone are required."}, status=400)

    order_id = f"DRN-{uuid.uuid4().hex[:10].upper()}"
    amount = drone.price

    order = Order.objects.create(
        order_id=order_id,
        user_name=user_name,
        user_email=user_email,
        user_phone=user_phone,
        order_type="drone",
        drone=drone,
        amount=amount,
        shipping_address=shipping_address,
        payment_status="pending",
        order_status="pending",
    )

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        rp_order = client.order.create(
            {
                "amount": int(amount * 100),
                "currency": "INR",
                "receipt": order.order_id,
                "payment_capture": 1,
            }
        )
    except Exception as exc:
        order.payment_status = "failed"
        order.save(update_fields=["payment_status"])
        return JsonResponse({"error": f"Payment gateway error: {str(exc)}"}, status=500)

    order.razorpay_order_id = rp_order["id"]
    order.save(update_fields=["razorpay_order_id"])

    return JsonResponse(
        {
            "success": True,
            "key": settings.RAZORPAY_KEY_ID,
            "razorpay_order_id": rp_order["id"],
            "amount": rp_order["amount"],
            "currency": rp_order["currency"],
            "order_ref": order.order_id,
            "drone_name": drone.name,
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def verify_drone_payment(request):
    """Verify drone payment and confirm order."""
    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return JsonResponse({"error": "Missing payment details."}, status=400)

    order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id, order_type="drone")

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
        )
    except razorpay.errors.SignatureVerificationError:
        order.payment_status = "failed"
        order.save(update_fields=["payment_status"])
        return JsonResponse({"error": "Payment signature verification failed."}, status=400)

    order.payment_status = "paid"
    order.order_status = "confirmed"
    order.razorpay_payment_id = razorpay_payment_id
    order.save(update_fields=["payment_status", "order_status", "razorpay_payment_id"])

    return JsonResponse(
        {
            "success": True,
            "redirect_url": f"/order/success/{order.order_id}/",
        }
    )


def customer_support(request):
    """Customer support page view"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        support_type = request.POST.get('support_type')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        priority = request.POST.get('priority')
        whatsapp_number = request.POST.get('whatsapp_number')
        
        # Create support request
        support_request = CustomerSupport.objects.create(
            name=name,
            email=email,
            phone=phone,
            support_type=support_type,
            subject=subject,
            message=message,
            priority=priority,
            whatsapp_number=whatsapp_number
        )
        
        messages.success(request, 'Your support request has been submitted successfully. We will contact you soon!')
        return redirect('notes:customer_support')
    
    return render(request, 'customer_support.html')


def create_order(request, product_id=None):
    """Create order for study materials with Razorpay integration"""
    if request.method == 'POST':
        try:
            # Get product if product_id is provided
            if product_id:
                product = get_object_or_404(Product, id=product_id)
                amount = float(product.price) if product.price else 1.0
                order_type = 'study_material'
            else:
                # Generic order creation
                order_type = request.POST.get('order_type', 'study_material')
                amount_str = request.POST.get('amount', '1')
                amount = float(amount_str) if amount_str else 1.0
            
            # Generate unique order ID
            order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            
            # Get user information
            user_name = request.POST.get('user_name', '')
            user_email = request.POST.get('user_email', '')
            user_phone = request.POST.get('user_phone', '')
            
            # Create order
            order = Order.objects.create(
                order_id=order_id,
                user_name=user_name,
                user_email=user_email,
                user_phone=user_phone,
                order_type=order_type,
                amount=amount
            )
            
            # Set product if provided
            if product_id:
                order.study_material = product
            
            order.save()
            
            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Create Razorpay order
            if amount is None:
                amount = 1.0  # Default amount
            
            razorpay_order = client.order.create({
                'amount': int(float(amount) * 100),  # Convert to paise
                'currency': 'INR',
                'receipt': order_id,
                'notes': f'Order for {order_type}',
                'payment_capture': '1'
            })
            
            # Save Razorpay order ID
            order.razorpay_order_id = razorpay_order['id']
            order.save()
            
            return JsonResponse({
                'success': True,
                'key': settings.RAZORPAY_KEY_ID,
                'razorpay_order_id': razorpay_order['id'],
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
                'order_ref': order_id,
                'product_name': product.title if product_id else 'Study Material'
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Failed to create order: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def create_order_generic(request):
    """Create order for drone/study material/workshop"""
    if request.method == 'POST':
        order_type = request.POST.get('order_type')
        item_id = request.POST.get('item_id')
        user_name = request.POST.get('user_name')
        user_email = request.POST.get('user_email')
        user_phone = request.POST.get('user_phone')
        amount = request.POST.get('amount')
        shipping_address = request.POST.get('shipping_address')
        billing_address = request.POST.get('billing_address')
        
        # Generate unique order ID
        import uuid
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Create order
        order = Order.objects.create(
            order_id=order_id,
            user_name=user_name,
            user_email=user_email,
            user_phone=user_phone,
            order_type=order_type,
            amount=amount,
            shipping_address=shipping_address,
            billing_address=billing_address
        )
        
        # Set the related item based on order type
        if order_type == 'drone':
            order.drone_id = item_id
        elif order_type == 'workshop':
            order.workshop_id = item_id
        elif order_type == 'study_material':
            order.study_material_id = item_id
        
        order.save()
        
        messages.success(request, 'Order created successfully! Please proceed to payment.')
        return redirect('notes:payment', order_id=order_id)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def payment_view(request, order_id):
    """Payment page view"""
    order = get_object_or_404(Order, order_id=order_id)
    
    if request.method == 'POST':
        # Check if Razorpay order already exists
        if order.razorpay_order_id:
            # Return existing order details
            return JsonResponse({
                'success': True,
                'key': settings.RAZORPAY_KEY_ID,
                'razorpay_order_id': order.razorpay_order_id,
                'amount': int(order.amount * 100),  # Already in paise
                'currency': 'INR',
                'order_ref': order.order_id,
                'product_name': order.study_material.title if order.study_material else 'Study Material'
            })
        
        # Process payment - create new Razorpay order only if doesn't exist
        try:
            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Create Razorpay order
            razorpay_order = client.order.create({
                'amount': int(order.amount * 100),  # Convert to paise
                'currency': 'INR',
                'receipt': order.order_id,
                'notes': f'Order for {order.order_type}',
                'payment_capture': '1'
            })
            
            # Save Razorpay IDs
            order.razorpay_order_id = razorpay_order['id']
            order.save()
            
            return JsonResponse({
                'success': True,
                'key': settings.RAZORPAY_KEY_ID,
                'razorpay_order_id': razorpay_order['id'],
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
                'order_ref': order.order_id,
                'product_name': order.study_material.title if order.study_material else 'Study Material'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return render(request, 'payment.html', {'order': order})


def payment_callback(request):
    """Razorpay payment callback"""
    if request.method == 'POST':
        try:
            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Verify payment
            razorpay_order = client.order.fetch(request.POST.get('razorpay_order_id'))
            
            if razorpay_order['status'] == 'captured':
                # Payment successful
                order = Order.objects.get(razorpay_order_id=request.POST.get('razorpay_order_id'))
                order.payment_status = 'paid'
                order.order_status = 'confirmed'
                order.razorpay_payment_id = request.POST.get('razorpay_payment_id')
                order.save()
                
                # Create workshop registration if payment for workshop
                if order.order_type == 'workshop' and order.workshop:
                    WorkshopRegistration.objects.create(
                        workshop=order.workshop,
                        name=order.user_name,
                        email=order.user_email,
                        mobile=order.user_phone,
                        form_data={}
                    )
                
                return JsonResponse({'success': True, 'message': 'Payment successful'})
            else:
                # Payment failed
                order = Order.objects.get(razorpay_order_id=request.POST.get('razorpay_order_id'))
                order.payment_status = 'failed'
                order.save()
                
                return JsonResponse({'success': False, 'message': 'Payment failed'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def order_success(request):
    """Order success page"""
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, order_id=order_id)
    
    return render(request, 'order_success.html', {'order': order})


def my_orders(request):
    """User's orders page"""
    if request.user.is_authenticated:
        orders = Order.objects.filter(user_email=request.user.email).order_by('-created_at')
        return render(request, 'my_orders.html', {'orders': orders})
    else:
        return redirect('notes:home')


def test_page(request):
    """Test page to check Django template processing"""
    return render(request, "test_template.html")


def simple_test(request):
    """Simple test page to verify CSS and Django templates"""
    return render(request, "simple_test.html")


def home_minimal(request):
    """Minimal home page to test CSS"""
    featured_products = Product.objects.all()[:6]
    return render(request, "index_minimal.html", {"featured_products": featured_products})


def about(request):
    """About page view"""
    return render(request, "about.html")


def services(request):
    """Services page view"""
    featured_products = Product.objects.all()[:3]  # Get first 3 products as featured
    return render(request, "service.html", {"featured_products": featured_products})


def projects(request):
    """Projects page view"""
    projects = Project.objects.filter(active=True)
    featured_projects = projects.filter(featured=True)
    return render(request, "project.html", {
        "projects": projects,
        "featured_projects": featured_projects
    })


def project_detail(request, slug):
    """Project detail page view"""
    project = get_object_or_404(Project, slug=slug, active=True)
    return render(request, "project_detail.html", {"project": project})


def features(request):
    """Features page view"""
    return render(request, "feature.html")


def contact(request):
    """Contact page view with form handling"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        service_type = request.POST.get('service_type', 'other')
        message = request.POST.get('message', '').strip()
        
        # Validate required fields
        if name and email and mobile:
            # Create contact record
            Contact.objects.create(
                name=name,
                email=email,
                mobile=mobile,
                service_type=service_type,
                message=message
            )
            
            messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            return redirect('notes:contact')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, "contact.html")


def team(request):
    """Team page view"""
    return render(request, "team.html")


def testimonial(request):
    """Testimonial page view"""
    return render(request, "testimonial.html")

def drone_shop(request):
    """Drone shop page view"""
    drones = Drone.objects.filter(active=True).order_by("-featured", "-created_at")
    return render(request, "drone_shop.html", {"drones": drones})

def workshops(request):
    """Workshops page view"""
    workshops = Workshop.objects.filter(active=True)
    return render(request, "workshops.html", {"workshops": workshops})


def workshop_register(request, slug):
    """Workshop registration page (payment initiated via AJAX)."""
    workshop = get_object_or_404(Workshop, slug=slug, active=True)
    
    # Check if registration is still open
    if timezone.now() > workshop.registration_deadline:
        messages.error(request, "Registration for this workshop has closed.")
        return redirect('notes:workshops')
    
    # Check if workshop is full
    if workshop.registrations.count() >= workshop.max_participants:
        messages.error(request, "This workshop is fully booked.")
        return redirect('notes:workshops')
    
    form_fields = workshop.form_fields.all().order_by("order")

    return render(request, "workshop_register.html", {
        "workshop": workshop,
        "form_fields": form_fields
    })


@require_http_methods(["POST"])
def create_workshop_order(request, slug):
    """Create Razorpay order for workshop registration."""
    workshop = get_object_or_404(Workshop, slug=slug, active=True)

    if timezone.now() > workshop.registration_deadline:
        return JsonResponse({"error": "Registration for this workshop has closed."}, status=400)
    if workshop.registrations.count() >= workshop.max_participants:
        return JsonResponse({"error": "This workshop is fully booked."}, status=400)

    name = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip().lower()
    mobile = request.POST.get("mobile", "").strip()
    if not name or not email or not mobile:
        return JsonResponse({"error": "Name, email, and mobile are required."}, status=400)

    if WorkshopRegistration.objects.filter(workshop=workshop, email=email).exists():
        return JsonResponse({"error": "You have already registered for this workshop."}, status=400)

    form_data = {}
    for field in workshop.form_fields.all().order_by("order"):
        if field.field_type == "checkbox":
            form_data[field.field_name] = request.POST.getlist(field.field_name)
        else:
            form_data[field.field_name] = request.POST.get(field.field_name, "")

    amount = workshop.entry_fee if workshop.entry_fee else Decimal("0.00")
    if amount <= 0:
        return JsonResponse({"error": "Workshop entry fee is not set. Please contact support."}, status=400)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        rp_order = client.order.create(
            {
                "amount": int(amount * 100),
                "currency": "INR",
                "receipt": f"workshop_{uuid.uuid4().hex[:10]}",
                "payment_capture": 1,
            }
        )
    except Exception as exc:
        return JsonResponse({"error": f"Payment gateway error: {str(exc)}"}, status=500)

    pending = request.session.get("pending_workshop_registrations", {})
    pending[rp_order["id"]] = {
        "workshop_id": workshop.id,
        "name": name,
        "email": email,
        "mobile": mobile,
        "amount": str(amount),
        "form_data": form_data,
    }
    request.session["pending_workshop_registrations"] = pending
    request.session.modified = True

    return JsonResponse(
        {
            "success": True,
            "key": settings.RAZORPAY_KEY_ID,
            "razorpay_order_id": rp_order["id"],
            "amount": rp_order["amount"],
            "currency": rp_order["currency"],
            "workshop_title": workshop.title,
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def verify_workshop_payment(request):
    """Verify Razorpay payment and finalize registration."""
    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return JsonResponse({"error": "Missing payment details."}, status=400)

    pending = request.session.get("pending_workshop_registrations", {})
    payload = pending.get(razorpay_order_id)
    if not payload:
        return JsonResponse({"error": "Session expired. Please register again."}, status=400)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
        )
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({"error": "Payment signature verification failed."}, status=400)

    workshop = get_object_or_404(Workshop, id=payload["workshop_id"], active=True)

    registration, created = WorkshopRegistration.objects.get_or_create(
        workshop=workshop,
        email=payload["email"],
        defaults={
            "name": payload["name"],
            "mobile": payload["mobile"],
            "form_data": payload["form_data"],
            "payment_status": "paid",
            "amount_paid": Decimal(payload["amount"]),
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
        },
    )
    if not created:
        registration.payment_status = "paid"
        registration.amount_paid = Decimal(payload["amount"])
        registration.razorpay_order_id = razorpay_order_id
        registration.razorpay_payment_id = razorpay_payment_id
        registration.save()

    pending.pop(razorpay_order_id, None)
    request.session["pending_workshop_registrations"] = pending
    request.session.modified = True

    return JsonResponse(
        {
            "success": True,
            "redirect_url": f"/workshops/registration-success/{registration.id}/",
        }
    )


def workshop_registration_success(request, registration_id):
    registration = get_object_or_404(
        WorkshopRegistration, id=registration_id, payment_status="paid"
    )
    return render(
        request,
        "workshop_registration_success.html",
        {"registration": registration},
    )


def download_workshop_ticket(request, registration_id):
    registration = get_object_or_404(
        WorkshopRegistration, id=registration_id, payment_status="paid"
    )

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 70

    p.setFont("Helvetica-Bold", 20)
    p.drawString(60, y, "DPRAMP Workshop Entry Ticket")
    y -= 30
    p.setFont("Helvetica", 12)
    p.drawString(60, y, f"Ticket ID: {registration.ticket_id}")
    y -= 35

    lines = [
        f"Name: {registration.name}",
        f"Email: {registration.email}",
        f"Mobile: {registration.mobile}",
        f"Workshop: {registration.workshop.title}",
        f"Date: {registration.workshop.date.strftime('%d %b %Y, %I:%M %p')}",
        f"Location: {registration.workshop.location}",
        f"Instructor: {registration.workshop.instructor}",
        f"Entry Fee Paid: INR {registration.amount_paid}",
        f"Payment ID: {registration.razorpay_payment_id}",
    ]
    for line in lines:
        p.drawString(60, y, line)
        y -= 22

    p.setFont("Helvetica-Oblique", 10)
    p.drawString(60, 90, "Please carry this ticket at entry gate.")
    p.drawString(60, 74, "Generated by DPRAMP workshop registration system.")

    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="workshop-ticket-{registration.ticket_id}.pdf"'
    )
    return response


def workshops_conducted(request):
    """Workshops conducted page view"""
    return render(request, "workshops_conducted.html")


def product_list(request):
    """Product listing page - show all PDFs category-wise"""
    categories = Category.objects.all()
    return render(request, "products/product_list.html", {"categories": categories})


def product_detail(request, slug):
    """Product detail page - show individual PDF details"""
    product = get_object_or_404(Product, slug=slug)
    preview_images = product.preview_images.all().order_by("order")
    return render(
        request,
        "products/product_detail.html",
        {"product": product, "preview_images": preview_images},
    )


def create_order_product(request, product_id):
    """Create order and initiate payment"""
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    product = get_object_or_404(Product, id=product_id)

    # Get form data
    name = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip()

    if not name or not email:
        return JsonResponse({"error": "Name and email are required"}, status=400)

    # Create Razorpay order
    print(f"Initializing Razorpay client...")
    print(f"Key ID: {settings.RAZORPAY_KEY_ID}")
    print(f"Key Secret: {settings.RAZORPAY_KEY_SECRET[:10]}...")
    
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )
    print("Razorpay client initialized successfully")

    try:
        print(f"Creating order with key: {settings.RAZORPAY_KEY_ID}")
        print(f"Product price: {product.price}")
        razorpay_order = client.order.create(
            {
                "amount": int(product.price * 100),  # Convert to paise
                "currency": "INR",
                "receipt": f"receipt_{uuid.uuid4().hex[:8]}",
                "payment_capture": 1,
            }
        )
        print(f"Order created successfully: {razorpay_order}")
    except Exception as e:
        print(f"Razorpay error: {str(e)}")
        return JsonResponse({"error": f"Failed to create payment order: {str(e)}"}, status=500)

    # Create order in database
    order = Order.objects.create(
        name=name,
        email=email,
        product=product,
        payment_id=razorpay_order["id"],
        amount=product.price,
        payment_status="pending",
    )

    # Use Razorpay payment link for direct collection
    return JsonResponse(
        {
            "order_id": order.id,
            "razorpay_order_id": razorpay_order["id"],
            "amount": razorpay_order["amount"],
            "currency": razorpay_order["currency"],
            "key": settings.RAZORPAY_KEY_ID,
            "payment_link": settings.RAZORPAY_PAYMENT_LINK,
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def payment_callback(request):
    """Handle Razorpay payment callback"""
    try:
        # Get payment details
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_signature = request.POST.get("razorpay_signature")

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return JsonResponse({"error": "Missing payment details"}, status=400)

        # Verify payment signature
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        try:
            client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "razorpay_signature": razorpay_signature,
                }
            )
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"error": "Invalid payment signature"}, status=400)

        # Update order status
        order = get_object_or_404(Order, payment_id=razorpay_order_id)
        order.payment_status = "completed"
        order.save()

        # Create download token
        download_token = DownloadToken.objects.create(order=order)

        return JsonResponse(
            {
                "success": True,
                "order_id": order.id,
                "download_token": str(download_token.token),
                "redirect_url": f"/payment-success/{order.id}/",
            }
        )

    except Exception as e:
        return JsonResponse({"error": "Payment processing failed"}, status=500)


def payment_success(request, order_id):
    """Payment success page with auto-download"""
    order = get_object_or_404(Order, id=order_id, payment_status="completed")

    try:
        download_token = order.download_token
    except DownloadToken.DoesNotExist:
        download_token = DownloadToken.objects.create(order=order)

    return render(
        request,
        "products/payment_success.html",
        {"order": order, "download_token": download_token.token},
    )


def download_pdf(request, token):
    """Secure PDF download with token validation"""
    try:
        download_token = get_object_or_404(DownloadToken, token=token)

        # Validate token
        if download_token.is_expired():
            return render(
                request,
                "products/download_error.html",
                {"error": "Download link has expired. Please contact support."},
                status=410,
            )

        # Check payment status
        if download_token.order.payment_status != "completed":
            return render(
                request,
                "products/download_error.html",
                {
                    "error": "Payment not completed. Please complete your purchase first."
                },
                status=403,
            )

        # Serve the PDF file
        pdf_path = download_token.order.product.pdf_file.path
        if not os.path.exists(pdf_path):
            return render(
                request,
                "products/download_error.html",
                {"error": "PDF file not found. Please contact support."},
                status=404,
            )

        # Open and serve the file
        with open(pdf_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="application/pdf")
            response["Content-Disposition"] = (
                f'attachment; filename="{download_token.order.product.title}.pdf"'
            )
            return response

    except Exception as e:
        return render(
            request,
            "products/download_error.html",
            {"error": "Download failed. Please try again or contact support."},
            status=500,
        )
