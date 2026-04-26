from django.core.management.base import BaseCommand
from django.utils.text import slugify
from notes.models import Category, Product, ProductImage
from django.core.files import File
import os
from django.conf import settings


class Command(BaseCommand):
    help = "Create sample categories and products for testing"

    def handle(self, *args, **options):
        # Create sample categories
        categories_data = [
            {
                "name": "Programming",
                "description": "Programming languages and software development notes",
            },
            {
                "name": "Data Science",
                "description": "Data analysis, machine learning, and AI notes",
            },
            {
                "name": "Web Development",
                "description": "Frontend and backend web development resources",
            },
            {
                "name": "Mobile Development",
                "description": "iOS and Android app development notes",
            },
        ]

        self.stdout.write("Creating categories...")
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={
                    "slug": slugify(cat_data["name"]),
                    "description": cat_data["description"],
                },
            )
            if created:
                self.stdout.write(f"Created category: {category.name}")
            else:
                self.stdout.write(f"Category already exists: {category.name}")

        # Create sample products
        products_data = [
            {
                "title": "Python Programming Complete Guide",
                "description": "Comprehensive Python programming guide covering basics to advanced concepts including OOP, data structures, algorithms, and practical projects.",
                "price": 299.00,
                "category": "Programming",
                "thumbnail": "img/rough_imgs/python.png",
            },
            {
                "title": "JavaScript Modern Development",
                "description": "Learn modern JavaScript including ES6+, async programming, DOM manipulation, and popular frameworks like React and Vue.",
                "price": 349.00,
                "category": "Web Development",
                "thumbnail": "img/rough_imgs/service-1-1.png",
            },
            {
                "title": "Machine Learning Fundamentals",
                "description": "Introduction to machine learning algorithms, supervised and unsupervised learning, neural networks, and practical implementations.",
                "price": 499.00,
                "category": "Data Science",
                "thumbnail": "img/rough_imgs/NLP.png",
            },
            {
                "title": "React Native Mobile Apps",
                "description": "Build cross-platform mobile applications using React Native. Learn components, navigation, state management, and deployment.",
                "price": 399.00,
                "category": "Mobile Development",
                "thumbnail": "img/rough_imgs/mobile-application-development-on-laptop-screen-concept-background-app-coding-and-web-development-cross-platform-devices-smartphone-tablet-and-computer-vector.jpg",
            },
            {
                "title": "Data Structures and Algorithms",
                "description": "Master essential data structures and algorithms with detailed explanations, code examples, and interview preparation tips.",
                "price": 449.00,
                "category": "Programming",
                "thumbnail": "img/rough_imgs/DataAn.png",
            },
            {
                "title": "Django Web Development",
                "description": "Complete guide to Django framework including models, views, templates, authentication, APIs, and deployment strategies.",
                "price": 379.00,
                "category": "Web Development",
                "thumbnail": "img/rough_imgs/service-2-1.png",
            },
        ]

        self.stdout.write("Creating products...")
        for prod_data in products_data:
            category = Category.objects.get(name=prod_data["category"])

            product, created = Product.objects.get_or_create(
                title=prod_data["title"],
                defaults={
                    "slug": slugify(prod_data["title"]),
                    "description": prod_data["description"],
                    "price": prod_data["price"],
                    "category": category,
                    "thumbnail": prod_data["thumbnail"],
                    "pdf_file": "sample.pdf",  # Placeholder
                },
            )

            if created:
                self.stdout.write(f"Created product: {product.title}")

                # Add preview images (placeholder)
                preview_images = [
                    "img/rough_imgs/service-1-2.png",
                    "img/rough_imgs/service-1-3.png",
                    "img/rough_imgs/service-1-4.png",
                ]

                for i, img_path in enumerate(preview_images):
                    ProductImage.objects.create(
                        product=product, image=img_path, order=i + 1
                    )
            else:
                self.stdout.write(f"Product already exists: {product.title}")

        self.stdout.write(self.style.SUCCESS("Sample data setup completed!"))
