from django.contrib import admin
import csv
import datetime
from django.http import HttpResponse
from .models import Category, Product, Order, DownloadToken, ProductImage, Contact, Project, Workshop, WorkshopForm, WorkshopRegistration, Feature, Drone, CustomerSupport, WebsitePopup


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Study Material Categories Management
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 4
    max_num = 4
    fk_name = "product"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Study Materials Management
    list_display = ["title", "category", "price", "document_type_display", "created_at"]
    list_filter = ["category", "document_type", "created_at"]
    search_fields = ["title", "description"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductImageInline]
    readonly_fields = ["created_at", "file_extension", "file_icon", "updated_at"]
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("title", "slug", "category", "description", "price")
        }),
        ("Document Files", {
            "fields": ("document_file", "document_type", "pdf_file", "thumbnail")
        }),
        ("File Information", {
            "fields": ("file_extension", "file_icon"),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def document_type_display(self, obj):
        if obj.document_file:
            return f"{obj.get_document_type_display()} ({obj.file_extension})"
        elif obj.pdf_file:
            return "PDF (Legacy)"
        return "No file"
    document_type_display.short_description = "Document Type"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category")


@admin.register(DownloadToken)
class DownloadTokenAdmin(admin.ModelAdmin):
    list_display = ["token", "expires_at", "created_at", "is_used"]
    list_filter = ["created_at", "expires_at"]
    search_fields = ["token"]
    readonly_fields = ["token", "created_at", "expires_at"]

    def is_used(self, obj):
        return obj.is_expired()

    is_used.boolean = True
    is_used.short_description = "Used/Expired"


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "mobile", "service_type_display", "created_at"]
    list_filter = ["service_type", "created_at"]
    search_fields = ["name", "email", "mobile", "message"]
    readonly_fields = ["created_at"]
    actions = ["export_as_excel"]
    
    fieldsets = (
        ("Contact Information", {
            "fields": ("name", "email", "mobile", "service_type")
        }),
        ("Message", {
            "fields": ("message",)
        }),
        ("Timestamp", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )
    
    def service_type_display(self, obj):
        return obj.get_service_type_display()
    service_type_display.short_description = "Service Type"
    
    def export_as_excel(self, request, queryset):
        """
        Export selected contacts as Excel (CSV) file
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="contacts_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow(['Name', 'Email', 'Mobile', 'Service Type', 'Message', 'Created At'])
        
        # Write data
        for contact in queryset:
            writer.writerow([
                contact.name,
                contact.email,
                contact.mobile,
                contact.get_service_type_display(),
                contact.message,
                contact.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ])
        
        return response
    
    export_as_excel.short_description = "Export selected as Excel"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "project_type_display", "client_name", "featured", "active", "created_at"]
    list_filter = ["project_type", "featured", "active", "created_at"]
    search_fields = ["title", "description", "client_name", "technologies"]
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ["featured", "active"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        ("Project Information", {
            "fields": ("title", "slug", "project_type", "client_name")
        }),
        ("Content", {
            "fields": ("description", "technologies", "image", "case_study_link")
        }),
        ("Display Options", {
            "fields": ("featured", "active")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def project_type_display(self, obj):
        return obj.get_project_type_display()
    project_type_display.short_description = "Project Type"


class WorkshopFormInline(admin.TabularInline):
    model = WorkshopForm
    extra = 5
    min_num = 1
    fields = ['field_label', 'field_name', 'field_type', 'required', 'placeholder', 'options', 'order']


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ["title", "date", "location", "instructor", "active", "registrations_count"]
    list_filter = ["date", "active", "location"]
    search_fields = ["title", "description", "instructor", "location"]
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ["active"]
    readonly_fields = ["created_at", "registration_link"]
    inlines = [WorkshopFormInline]
    
    fieldsets = (
        ("Workshop Information", {
            "fields": ("title", "slug", "description", "active")
        }),
        ("Schedule & Location", {
            "fields": ("date", "location", "instructor", "max_participants", "registration_deadline")
        }),
        ("Registration Link", {
            "fields": ("registration_link",),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )
    
    def registration_link(self, obj):
        if obj.slug:
            link = f"/workshops/{obj.slug}/register/"
            return f'<a href="{link}" target="_blank">{link}</a>'
        return "Save workshop first"
    registration_link.short_description = "Registration Link"
    registration_link.allow_tags = True
    
    def registrations_count(self, obj):
        return obj.registrations.count()
    registrations_count.short_description = "Registrations"


@admin.register(WorkshopForm)
class WorkshopFormAdmin(admin.ModelAdmin):
    list_display = ["workshop", "field_label", "field_type", "required", "order"]
    list_filter = ["workshop", "field_type", "required"]
    search_fields = ["workshop__title", "field_label", "field_name"]
    list_editable = ["order"]


@admin.register(WorkshopRegistration)
class WorkshopRegistrationAdmin(admin.ModelAdmin):
    list_display = ["workshop", "name", "email", "mobile", "registered_at"]
    list_filter = ["workshop", "registered_at"]
    search_fields = ["workshop__title", "name", "email", "mobile"]
    readonly_fields = ["workshop", "name", "email", "mobile", "form_data", "registered_at"]
    actions = ["export_as_excel"]
    
    fieldsets = (
        ("Registration Information", {
            "fields": ("workshop", "name", "email", "mobile", "registered_at")
        }),
        ("Form Data", {
            "fields": ("form_data",),
            "classes": ("collapse",)
        }),
    )
    
    def export_as_excel(self, request, queryset):
        """
        Export workshop registrations as Excel (CSV) file
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="workshop_registrations_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        
        # Get all unique field names from form data
        all_fields = set()
        for registration in queryset:
            all_fields.update(registration.form_data.keys())
        all_fields = sorted(all_fields)
        
        # Write header
        header = ['Workshop', 'Name', 'Email', 'Mobile', 'Registered At'] + all_fields
        writer.writerow(header)
        
        # Write data
        for registration in queryset:
            row = [
                registration.workshop.title,
                registration.name,
                registration.email,
                registration.mobile,
                registration.registered_at.strftime("%Y-%m-%d %H:%M:%S")
            ]
            
            # Add form data
            for field in all_fields:
                row.append(registration.form_data.get(field, ''))
            
            writer.writerow(row)
        
        return response
    
    export_as_excel.short_description = "Export selected as Excel"


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ["title", "icon", "color", "scrolling", "order", "active", "created_at"]
    list_filter = ["color", "scrolling", "active", "created_at"]
    search_fields = ["title", "description"]
    list_editable = ["order", "active", "scrolling"]
    readonly_fields = ["created_at"]
    ordering = ["order", "created_at"]
    
    fieldsets = (
        ("Feature Information", {
            "fields": ("title", "description", "icon", "color")
        }),
        ("Display Options", {
            "fields": ("scrolling", "order", "active")
        }),
        ("Timestamps", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('order', 'created_at')


@admin.register(Drone)
class DroneAdmin(admin.ModelAdmin):
    list_display = ["name", "drone_type", "category", "price", "status", "featured", "active", "created_at"]
    list_filter = ["drone_type", "category", "status", "featured", "active", "created_at"]
    search_fields = ["name", "description", "brand", "model_number"]
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ["featured", "active", "status"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "slug", "description", "drone_type", "category", "brand", "model_number")
        }),
        ("Pricing & Status", {
            "fields": ("price", "status", "featured", "active")
        }),
        ("Media", {
            "fields": ("image", "gallery_images", "video_url")
        }),
        ("Technical Details", {
            "fields": ("specifications", "features")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def drone_type_display(self, obj):
        return obj.get_drone_type_display()
    drone_type_display.short_description = "Drone Type"


@admin.register(CustomerSupport)
class CustomerSupportAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "support_type", "priority", "status", "created_at"]
    list_filter = ["support_type", "priority", "status", "created_at"]
    search_fields = ["name", "email", "subject", "message"]
    list_editable = ["status", "priority"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        ("Customer Information", {
            "fields": ("name", "email", "phone", "whatsapp_number")
        }),
        ("Support Details", {
            "fields": ("support_type", "subject", "message", "priority")
        }),
        ("Status & Response", {
            "fields": ("status", "response", "resolved_at")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def support_type_display(self, obj):
        return obj.get_support_type_display()
    support_type_display.short_description = "Support Type"
    
    def priority_display(self, obj):
        return obj.get_priority_display()
    priority_display.short_description = "Priority"
    
    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = "Status"


@admin.register(WebsitePopup)
class WebsitePopupAdmin(admin.ModelAdmin):
    list_display = ["title", "popup_type", "is_active", "display_delay", "created_at"]
    list_filter = ["popup_type", "is_active", "show_once_per_session", "created_at"]
    search_fields = ["title", "action_text"]
    list_editable = ["is_active"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        ("Popup Information", {
            "fields": ("title", "popup_type", "is_active")
        }),
        ("Image Poster Settings", {
            "fields": ("poster_image",),
            "description": "Upload an image poster/banner (if popup_type is 'banner')"
        }),
        ("Modal Popup Settings", {
            "fields": ("modal_content",),
            "classes": ("collapse",),
            "description": "HTML content for modal popup (if popup_type is 'modal')"
        }),
        ("Action Link (Optional)", {
            "fields": ("action_link", "action_text"),
            "classes": ("collapse",)
        }),
        ("Display Settings", {
            "fields": ("display_delay", "show_once_per_session")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def popup_type_display(self, obj):
        return obj.get_popup_type_display()
    popup_type_display.short_description = "Popup Type"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Order Management
    list_display = ["order_id", "user_name", "user_email", "order_type", "amount", "payment_status", "order_status", "created_at"]
    list_filter = ["order_type", "payment_status", "order_status", "created_at"]
    search_fields = ["order_id", "user_name", "user_email", "razorpay_order_id"]
    readonly_fields = ["razorpay_order_id", "razorpay_payment_id", "created_at", "updated_at"]
    
    fieldsets = (
        ("Order Information", {
            "fields": ("order_id", "user_name", "user_email", "user_phone", "order_type")
        }),
        ("Item Details", {
            "fields": ("drone", "workshop", "study_material")
        }),
        ("Pricing", {
            "fields": ("amount", "currency")
        }),
        ("Payment Information", {
            "fields": ("razorpay_order_id", "razorpay_payment_id", "payment_status")
        }),
        ("Order Status", {
            "fields": ("order_status",)
        }),
        ("Address Information", {
            "fields": ("shipping_address", "billing_address")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def order_type_display(self, obj):
        return obj.get_order_type_display()
    order_type_display.short_description = "Order Type"
    
    def payment_status_display(self, obj):
        return obj.get_payment_status_display()
    payment_status_display.short_description = "Payment Status"
    
    def order_status_display(self, obj):
        return obj.get_order_status_display()
    order_status_display.short_description = "Order Status"
