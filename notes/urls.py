from django.urls import path
from . import views

app_name = "notes"

urlpatterns = [
    # Static pages
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("projects/", views.projects, name="projects"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    # Drone URLs
    path("drones/", views.drone_list, name="drone_list"),
    path("drones/<slug:slug>/", views.drone_detail, name="drone_detail"),
    path("support/", views.customer_support, name="customer_support"),
    # Payment and Order URLs
    path("order/create/", views.create_order, name="create_order"),
    path("payment/<str:order_id>/", views.payment_view, name="payment"),
    path("payment/callback/", views.payment_callback, name="payment_callback"),
    path("order/success/<str:order_id>/", views.order_success, name="order_success"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("features/", views.features, name="features"),
    path("contact/", views.contact, name="contact"),
    path("team/", views.team, name="team"),
    path("testimonial/", views.testimonial, name="testimonial"),
    # Test pages
    path("test/", views.test_page, name="test_page"),
    path("simple/", views.simple_test, name="simple_test"),
    path("minimal/", views.home_minimal, name="home_minimal"),
    # Product related URLs
    path("pdf-notes/", views.product_list, name="product_list"),
    path("pdf-notes/<slug:slug>/", views.product_detail, name="product_detail"),
    # Payment and download URLs
    path("create-order/<int:product_id>/", views.create_order, name="create_order"),
    path("payment-callback/", views.payment_callback, name="payment_callback"),
    path("payment-success/<int:order_id>/", views.payment_success, name="payment_success"),
    path("download/<uuid:token>/", views.download_pdf, name="download_pdf"),
    # Drone Shop URL
    path("drone-shop/", views.drone_shop, name="drone_shop"),
    path("workshops/", views.workshops, name="workshops"),
    path("workshops/<slug:slug>/register/", views.workshop_register, name="workshop_register"),
]
