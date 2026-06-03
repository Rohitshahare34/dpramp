from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse, Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.core.files import File
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db import IntegrityError
from decimal import Decimal
from io import BytesIO
import csv
import razorpay
import uuid
import os
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from .forms import (
    ScholarshipRegistrationForm,
    EngineeringCounsellingRegistrationForm,
)
from .models import (
    Category,
    Product,
    Order,
    DownloadToken,
    ProductImage,
    Contact,
    Project,
    Workshop,
    WorkshopForm,
    WorkshopRegistration,
    Feature,
    Drone,
    CustomerSupport,
    WebsitePopup,
    ScholarshipRegistration,
    EngineeringCounsellingRegistration,
)


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
                "amount": int(float(amount) * 100),  # Convert to paise
                "currency": "INR",
                "receipt": order_id,
                "notes": {"order_type": order_type},
                "payment_capture": 1,
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
                "amount": int(order.amount * 100),  # Convert to paise
                "currency": "INR",
                "receipt": order.order_id,
                "notes": {"order_type": order.order_type},
                "payment_capture": 1,
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


def privacy_policy(request):
    """Privacy Policy page view"""
    return render(request, "privacy_policy.html")


def terms_conditions(request):
    """Terms & Conditions page view"""
    return render(request, "terms_conditions.html")


def refund_policy(request):
    """Refund Policy page view"""
    return render(request, "refund_policy.html")


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
    """Workshops listing page view"""
    workshops = Workshop.objects.filter(active=True)
    return render(request, "workshops.html", {"workshops": workshops})


def _notify_counselling_lead(registration):
    """Email admin about a new engineering counselling registration."""
    recipients = getattr(settings, "COUNSELLING_ADMIN_EMAILS", None) or [
        "dpramptechsolution@gmail.com",
        "info@dpramp.com",
    ]
    status_label = registration.get_twelfth_status_display()
    branch = registration.get_branch_display_label()
    email_line = registration.email or "Not provided"
    body = (
        f"New Engineering Admission Counselling registration\n\n"
        f"Student Name: {registration.student_name}\n"
        f"Mobile: {registration.mobile_number}\n"
        f"Email: {email_line}\n"
        f"City: {registration.city}\n"
        f"12th Status: {status_label}\n"
        f"Interested Branch: {branch}\n"
        f"Submitted: {registration.created_at}\n"
    )
    send_mail(
        subject=f"New Counselling Lead — {registration.student_name}",
        message=body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@dpramp.com"),
        recipient_list=recipients,
        fail_silently=True,
    )


COUNSELLING_SUCCESS_MESSAGE = (
    "Thank you for registering. Our counselling team will contact you shortly."
)


@require_http_methods(["POST"])
def engineering_counselling_register(request):
    """AJAX endpoint for engineering admission counselling registration."""
    form = EngineeringCounsellingRegistrationForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"success": False, "errors": form.errors}, status=400)
    registration = form.save()
    _notify_counselling_lead(registration)
    return JsonResponse({"success": True, "message": COUNSELLING_SUCCESS_MESSAGE})


def counselling_registration(request):
    """Full-page engineering counselling registration (after 12th)."""
    submitted = request.GET.get("submitted") == "1"
    if request.method == "POST":
        form = EngineeringCounsellingRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save()
            _notify_counselling_lead(registration)
            return redirect(f"{reverse('notes:counselling_registration')}?submitted=1")
    else:
        form = EngineeringCounsellingRegistrationForm()
    return render(
        request,
        "counselling_registration.html",
        {
            "form": form,
            "counselling_submitted": submitted,
        },
    )


def workshop_registration(request):
    """Legacy URL — redirects to engineering counselling registration."""
    return redirect("notes:counselling_registration", permanent=False)


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


def scholarship_registration(request):
    if request.method == "POST":
        form = ScholarshipRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                registration = form.save()
                return redirect("notes:scholarship_success", registration_id=registration.id)
            except IntegrityError:
                form.add_error(
                    "parent_mobile_number",
                    "This Parent Contact No. is already registered.",
                )
    else:
        form = ScholarshipRegistrationForm()

    return render(request, "scholarship_registration.html", {"form": form})


def scholarship_success(request, registration_id):
    registration = get_object_or_404(ScholarshipRegistration, id=registration_id)
    return render(
        request,
        "scholarship_success.html",
        {
            "registration": registration,
            "whatsapp_group_link": "https://chat.whatsapp.com/Df3Mh2qEXycAUsDZr45W8Q",
        },
    )


def download_hall_ticket(request, registration_id):
    registration = get_object_or_404(ScholarshipRegistration, id=registration_id)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Outer frame
    p.setLineWidth(1.2)
    p.setStrokeColorRGB(0.08, 0.18, 0.45)
    p.roundRect(24, 24, width - 48, height - 48, 12, stroke=1, fill=0)

    # Header band
    p.setFillColorRGB(0.07, 0.14, 0.36)
    p.roundRect(24, height - 120, width - 48, 96, 12, stroke=0, fill=1)
    logo_path = os.path.join(settings.BASE_DIR, "DPRAMP", "img", "image.png")
    text_start_x = 42
    if os.path.exists(logo_path):
        p.setFillColorRGB(1, 1, 1)
        p.roundRect(38, height - 106, 62, 62, 8, stroke=0, fill=1)
        p.drawImage(
            ImageReader(logo_path),
            42,
            height - 102,
            width=54,
            height=54,
            preserveAspectRatio=True,
            mask="auto",
        )
        text_start_x = 112

    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 22)
    p.drawString(text_start_x, height - 64, "ULC - REGISTRATION CARD")
    p.setFont("Helvetica-Bold", 13)
    p.drawString(text_start_x, height - 86, "Mega Education Fair & Scholarship Test 2026")
    p.setFont("Helvetica", 9.5)
    p.drawString(text_start_x, height - 102, "Universal Learning Center")
    p.setFont("Helvetica", 10)
    p.drawRightString(width - 42, height - 86, f"Roll No: {registration.roll_number}")

    registration_dt = timezone.localtime(registration.registration_datetime)
    reg_date_str = registration_dt.strftime("%d-%m-%Y")

    # Meta row
    p.setFillColorRGB(0.95, 0.97, 1)
    p.roundRect(36, height - 160, width - 72, 30, 6, stroke=0, fill=1)
    p.setFillColorRGB(0.08, 0.18, 0.45)
    p.setFont("Helvetica", 9.5)
    p.drawString(44, height - 142, f"Registration Date: {reg_date_str}")
    p.drawRightString(width - 44, height - 142, f"Verification ID: {registration.roll_number}")

    y = height - 191

    # Photo card
    p.setStrokeColorRGB(0.75, 0.8, 0.92)
    p.roundRect(width - 190, y - 118, 145, 145, 8, stroke=1, fill=0)
    p.setFillColorRGB(0.5, 0.55, 0.68)
    p.setFont("Helvetica", 9)
    p.drawCentredString(width - 118, y - 106, "Student Photo")
    if registration.student_photo and registration.student_photo.path and os.path.exists(registration.student_photo.path):
        p.drawImage(
            ImageReader(registration.student_photo.path),
            width - 184,
            y - 112,
            width=133,
            height=133,
            preserveAspectRatio=True,
            mask="auto",
        )

    # Candidate Details card
    p.setFillColorRGB(0.97, 0.98, 1)
    p.roundRect(36, y - 180, width - 245, 205, 10, stroke=0, fill=1)
    p.setFillColorRGB(0.08, 0.18, 0.45)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(46, y + 6, "Candidate Profile")

    p.setFont("Helvetica", 10)
    label_x = 46
    value_x = 170
    line_y = y - 14
    lines = [
        ("Full Name", registration.full_name),
        ("Parent/Guardian", registration.parent_guardian_name),
        ("Age", str(registration.age)),
        ("Class", registration.student_class),
        ("School/College", registration.school_name),
        ("City", registration.city),
        ("Email", registration.email_id),
        ("Parent Contact", registration.parent_mobile_number),
    ]
    for label, value in lines:
        p.setFillColorRGB(0.16, 0.23, 0.4)
        p.drawString(label_x, line_y, f"{label}:")
        p.setFillColorRGB(0.05, 0.09, 0.2)
        p.drawString(value_x, line_y, str(value))
        line_y -= 22

    # Center details (no exam date/time)
    center_y = y - 218
    p.setFillColorRGB(0.97, 0.99, 0.97)
    p.roundRect(36, center_y - 62, width - 72, 82, 10, stroke=0, fill=1)
    p.setFillColorRGB(0.1, 0.35, 0.12)
    p.setFont("Helvetica-Bold", 11)
    p.drawString(46, center_y + 4, "Test Center Information")
    p.setFillColorRGB(0.12, 0.18, 0.12)
    p.setFont("Helvetica", 10)
    p.drawString(46, center_y - 16, "Universal Learning Center")
    p.drawString(46, center_y - 34, "Please contact institute office for schedule updates.")

    # Institute branding + contact information
    info_y = center_y - 74
    p.setFillColorRGB(0.95, 0.97, 1.0)
    p.roundRect(36, info_y - 64, width - 72, 78, 10, stroke=0, fill=1)
    p.setFillColorRGB(0.08, 0.18, 0.45)
    p.setFont("Helvetica-Bold", 10.5)
    p.drawString(46, info_y - 2, "Institute Information")
    p.setFont("Helvetica", 9.2)
    p.setFillColorRGB(0.10, 0.15, 0.30)
    p.drawString(46, info_y - 18, "Programs: IIT-JEE | NEET | CET | XI-XII Science")
    p.drawString(46, info_y - 33, "Branch 1: IT Park, Gayatri Nagar")
    p.drawString(300, info_y - 33, "Branch 2: Nandanvan, Ganesh Nagar")
    p.drawString(46, info_y - 48, "Helpdesk: +91 9322859474 / +91 9673248000")

    # Instructions block
    inst_y = info_y - 82
    p.setFillColorRGB(1, 0.99, 0.95)
    p.roundRect(36, inst_y - 84, width - 72, 98, 10, stroke=0, fill=1)
    p.setFillColorRGB(0.56, 0.33, 0.0)
    p.setFont("Helvetica-Bold", 11)
    p.drawString(46, inst_y - 2, "Instructions")
    p.setFillColorRGB(0.25, 0.2, 0.05)
    p.setFont("Helvetica", 9.5)
    instructions = [
        "1. Carry this registration card and one valid ID proof.",
        "2. Mobile phones and smart devices are not allowed in test hall.",
        "3. Keep this card safely for verification at the center.",
        "4. Follow all guidance shared by Universal Learning Center staff.",
    ]
    text_y = inst_y - 22
    for line in instructions:
        p.drawString(46, text_y, line)
        text_y -= 16

    # Footer signature strip
    p.setFillColorRGB(0.93, 0.95, 0.99)
    p.roundRect(36, 38, width - 72, 38, 8, stroke=0, fill=1)
    p.setFillColorRGB(0.1, 0.17, 0.33)
    p.setFont("Helvetica", 9)
    p.drawString(46, 58, "Authorized by Universal Learning Center")
    p.drawRightString(width - 46, 58, "Universal Learning Center | Scholarship Desk")
    p.setFont("Helvetica-Oblique", 8.5)
    p.drawString(46, 45, "This is a system-generated Registration Card.")

    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "-", registration.full_name.strip()).strip("-") or "student"
    response["Content-Disposition"] = (
        f'attachment; filename="registration-card-{safe_name}-{registration.roll_number}.pdf"'
    )
    return response


@staff_member_required
def scholarship_admin_dashboard(request):
    queryset = ScholarshipRegistration.objects.all().order_by("registration_datetime")

    class_filter = request.GET.get("class", "").strip()
    city_filter = request.GET.get("city", "").strip()
    school_filter = request.GET.get("school", "").strip()

    if class_filter:
        queryset = queryset.filter(student_class=class_filter)
    if city_filter:
        queryset = queryset.filter(city__icontains=city_filter)
    if school_filter:
        queryset = queryset.filter(school_name__icontains=school_filter)

    if request.GET.get("export") == "1":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="scholarship_registrations.csv"'
        writer = csv.writer(response)
        writer.writerow(
            [
                "Roll Number",
                "Student Name",
                "Parent/Guardian Name",
                "Age",
                "Date of Birth",
                "Gender",
                "Parent Contact (WhatsApp)",
                "Email ID",
                "Class",
                "School Name",
                "City",
                "Medium",
                "Address",
                "Mobile Number (System)",
                "WhatsApp Number (System)",
                "Registration Date",
            ]
        )
        for reg in queryset:
            writer.writerow(
                [
                    reg.roll_number,
                    reg.full_name,
                    reg.parent_guardian_name,
                    reg.age,
                    reg.date_of_birth.strftime("%Y-%m-%d") if reg.date_of_birth else "",
                    reg.get_gender_display(),
                    reg.parent_mobile_number,
                    reg.email_id,
                    reg.student_class,
                    reg.school_name,
                    reg.city,
                    reg.get_medium_display(),
                    reg.address,
                    reg.mobile_number,
                    reg.whatsapp_number,
                    reg.registration_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )
        return response

    context = {
        "registrations": queryset[:500],
        "class_filter": class_filter,
        "city_filter": city_filter,
        "school_filter": school_filter,
    }
    return render(request, "scholarship_admin_dashboard.html", context)


def product_list(request):
    """Product listing page - show all PDFs category-wise"""
    categories = Category.objects.all()
    return render(request, "products/product_list.html", {"categories": categories})


def product_detail(request, slug):
    """Product detail page - show individual PDF details"""
    product = get_object_or_404(Product, slug=slug)
    # Only render images that really exist in storage to avoid 404s.
    preview_images = [
        image
        for image in product.preview_images.all().order_by("order")
        if image.image and default_storage.exists(image.image.name)
    ]
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
