import uuid
from datetime import datetime, timedelta
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = "Study Material Category"
        verbose_name_plural = "Study Material Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('ppt', 'PowerPoint (PPT)'),
        ('doc', 'Word Document (DOC)'),
        ('docx', 'Word Document (DOCX)'),
        ('pptx', 'PowerPoint (PPTX)'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE
    )
    document_file = models.FileField(upload_to="documents/", null=True, blank=True)
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPE_CHOICES, default='pdf')
    pdf_file = models.FileField(upload_to="pdfs/", null=True, blank=True)  # Keep old field for migration
    thumbnail = models.ImageField(upload_to="thumbnails/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Study Material"
        verbose_name_plural = "Study Materials"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-detect document type from file extension
        if self.document_file:
            file_extension = self.document_file.name.split('.')[-1].lower()
            if file_extension in ['pdf', 'ppt', 'doc', 'docx', 'pptx']:
                self.document_type = file_extension
        
        # Migrate from old pdf_file to new document_file if needed
        if self.pdf_file and not self.document_file:
            self.document_file = self.pdf_file
            self.document_type = 'pdf'
        
        super().save(*args, **kwargs)
    
    @property
    def file_extension(self):
        """Get file extension for display"""
        if self.document_file:
            return self.document_file.name.split('.')[-1].upper()
        elif self.pdf_file:
            return 'PDF'
        return 'FILE'
    
    @property
    def file_icon(self):
        """Get appropriate icon based on file type"""
        if self.document_type == 'pdf' or (self.pdf_file and not self.document_file):
            return 'fas fa-file-pdf'
        elif self.document_type in ['ppt', 'pptx']:
            return 'fas fa-file-powerpoint'
        elif self.document_type in ['doc', 'docx']:
            return 'fas fa-file-word'
        else:
            return 'fas fa-file'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="preview_images"
    )
    image = models.ImageField(upload_to="preview_images/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]




class DownloadToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Download Token"
        verbose_name_plural = "Download Tokens"
        ordering = ["-expires_at"]

    def __str__(self):
        return f"{self.token}"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_used_boolean(self):
        return self.is_used


class Contact(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('iot', 'IoT Solutions'),
        ('drone', 'Drone Technology'),
        ('arvr', 'AR/VR Development'),
        ('software', 'Software Development'),
        ('consulting', 'Consulting'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES, default='other')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contact Us"
        verbose_name_plural = "Contact Us Submissions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.email}"


class Project(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('web', 'Web Development'),
        ('app', 'App Development'),
        ('iot', 'IoT Solutions'),
        ('drone', 'Drone Technology'),
        ('arvr', 'AR/VR Development'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default='other')
    client_name = models.CharField(max_length=100, blank=True)
    technologies = models.CharField(max_length=200, help_text="Technologies used (comma separated)")
    image = models.ImageField(upload_to="projects/", null=True, blank=True)
    case_study_link = models.URLField(blank=True, help_text="Link to detailed case study")
    featured = models.BooleanField(default=False, help_text="Show in featured projects")
    active = models.BooleanField(default=True, help_text="Show on website")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("project_detail", kwargs={"slug": self.slug})


class Workshop(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    instructor = models.CharField(max_length=100)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_participants = models.PositiveIntegerField(default=50)
    registration_deadline = models.DateTimeField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Workshop"
        verbose_name_plural = "Workshops"
        ordering = ["date"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("workshop_register", kwargs={"slug": self.slug})


class WorkshopForm(models.Model):
    FIELD_TYPE_CHOICES = [
        ('text', 'Text Input'),
        ('email', 'Email'),
        ('tel', 'Phone Number'),
        ('number', 'Number'),
        ('textarea', 'Text Area'),
        ('select', 'Dropdown'),
        ('radio', 'Radio Buttons'),
        ('checkbox', 'Checkboxes'),
        ('date', 'Date'),
        ('file', 'File Upload'),
    ]
    
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name="form_fields")
    field_label = models.CharField(max_length=200)
    field_name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES)
    required = models.BooleanField(default=True)
    placeholder = models.CharField(max_length=200, blank=True)
    options = models.TextField(blank=True, help_text="Comma separated options for select/radio/checkbox")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Workshop Form Field"
        verbose_name_plural = "Workshop Form Fields"
        ordering = ["order"]

    def __str__(self):
        return f"{self.workshop.title} - {self.field_label}"


class WorkshopRegistration(models.Model):
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name="registrations")
    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    form_data = models.JSONField(default=dict)
    ticket_id = models.CharField(max_length=32, blank=True, db_index=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed")],
        default="pending",
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    razorpay_order_id = models.CharField(max_length=100, blank=True, default="")
    razorpay_payment_id = models.CharField(max_length=100, blank=True, default="")
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Workshop Registration"
        verbose_name_plural = "Workshop Registrations"
        ordering = ["-registered_at"]
        unique_together = ['workshop', 'email']

    def __str__(self):
        return f"{self.name} - {self.workshop.title}"

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = f"WS-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class Feature(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100, help_text="Font Awesome icon class (e.g., 'fas fa-robot')")
    color = models.CharField(max_length=20, default="primary", help_text="Bootstrap color class (e.g., 'primary', 'success', 'info')")
    scrolling = models.BooleanField(default=False, help_text="Show in scrolling features section")
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Feature"
        verbose_name_plural = "Features"
        ordering = ["order"]

    def __str__(self):
        return self.title




class Drone(models.Model):
    DRONE_TYPE_CHOICES = [
        ('agriculture', 'Agriculture'),
        ('surveillance', 'Surveillance'),
        ('photography', 'Photography'),
        ('industrial', 'Industrial'),
        ('racing', 'Racing'),
        ('delivery', 'Delivery'),
        ('military', 'Military'),
        ('hobby', 'Hobby'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
        ('pre_order', 'Pre-Order'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    drone_type = models.CharField(max_length=20, choices=DRONE_TYPE_CHOICES, default='hobby')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, help_text="Category (e.g., Professional, Entry-level)")
    brand = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=50, blank=True)
    specifications = models.JSONField(default=dict, help_text="Technical specifications in JSON format")
    image = models.ImageField(upload_to="drones/", null=True, blank=True)
    gallery_images = models.JSONField(default=list, help_text="Additional gallery images URLs")
    video_url = models.URLField(blank=True, help_text="Product video URL")
    features = models.TextField(blank=True, help_text="Key features and capabilities")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    featured = models.BooleanField(default=False, help_text="Show on home page")
    active = models.BooleanField(default=True, help_text="Show on website")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Drone"
        verbose_name_plural = "Drones"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("drone_detail", kwargs={"slug": self.slug})


class CustomerSupport(models.Model):
    SUPPORT_TYPE_CHOICES = [
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('phone', 'Phone'),
        ('chat', 'Live Chat'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    support_type = models.CharField(max_length=20, choices=SUPPORT_TYPE_CHOICES, default='email')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="WhatsApp contact number")
    response = models.TextField(blank=True, help_text="Admin response to the support request")
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer Support"
        verbose_name_plural = "Customer Support Requests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject}"


class WebsitePopup(models.Model):
    """Website Popup/Poster Management"""
    POPUP_TYPE_CHOICES = [
        ('modal', 'Modal Popup'),
        ('banner', 'Image Banner/Poster'),
    ]
    
    title = models.CharField(max_length=200, help_text="Popup/Banner title for admin reference")
    popup_type = models.CharField(max_length=20, choices=POPUP_TYPE_CHOICES, default='modal')
    is_active = models.BooleanField(default=False, help_text="Enable/disable popup on website")
    
    # For Image Banner/Poster
    poster_image = models.ImageField(upload_to="popups/", null=True, blank=True, help_text="Upload poster/banner image")
    
    # For Modal Popup
    modal_content = models.TextField(blank=True, help_text="HTML content for modal popup (if type is modal)")
    
    # Optional link
    action_link = models.URLField(blank=True, null=True, help_text="Button/link URL (optional)")
    action_text = models.CharField(max_length=100, blank=True, default="Learn More", help_text="Button text")
    
    # Display settings
    display_delay = models.PositiveIntegerField(default=2000, help_text="Delay before showing popup (in milliseconds)")
    show_once_per_session = models.BooleanField(default=True, help_text="Show only once per browser session")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Website Popup/Poster"
        verbose_name_plural = "Website Popups/Posters"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({'Active' if self.is_active else 'Inactive'})"


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('drone', 'Drone Purchase'),
        ('workshop', 'Workshop Registration'),
        ('study_material', 'Study Material'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_id = models.CharField(max_length=100, unique=True, default='')
    user_name = models.CharField(max_length=200, default='')
    user_email = models.EmailField(default='')
    user_phone = models.CharField(max_length=20, blank=True, default='')
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='study_material')
    
    # For Drone Orders
    drone = models.ForeignKey(Drone, on_delete=models.SET_NULL, null=True, blank=True)
    
    # For Workshop Orders
    workshop = models.ForeignKey(Workshop, on_delete=models.SET_NULL, null=True, blank=True)
    
    # For Study Material Orders
    study_material = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    
    # Pricing
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    
    # Payment Gateway
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Order Status
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    
    # Address
    shipping_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order_id} - {self.user_name}"
