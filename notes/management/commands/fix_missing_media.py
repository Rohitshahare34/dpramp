"""
Repair broken Product / Drone / Project image paths by copying files into MEDIA_ROOT.
Run: python manage.py fix_missing_media
"""

from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from notes.models import Drone, Product, Project

BASE_DIR = Path(settings.BASE_DIR)
STATIC_IMG = BASE_DIR / "DPRAMP" / "img"
ROUGH = STATIC_IMG / "rough_imgs"


def first_existing(*paths):
    for path in paths:
        if path and path.is_file():
            return path
    return None


class Command(BaseCommand):
    help = "Copy missing images into media/ and fix database ImageField paths."

    def handle(self, *args, **options):
        fixed = 0

        product_sources = {
            "Python Programming Complete Guide": [
                ROUGH / "python.png",
                STATIC_IMG / "service-1.jpg",
            ],
            "JavaScript Modern Development": [
                ROUGH / "service-1-1.png",
                STATIC_IMG / "service-2.jpg",
            ],
            "Machine Learning Fundamentals": [
                ROUGH / "NLP.png",
            ],
            "React Native Mobile Apps": [
                ROUGH
                / "mobile-application-development-on-laptop-screen-concept-background-app-coding-and-web-development-cross-platform-devices-smartphone-tablet-and-computer-vector.jpg",
            ],
            "Data Structures and Algorithms": [
                ROUGH / "DataAn.png",
                ROUGH / "dataanalyst.png",
            ],
            "Django Web Development": [
                STATIC_IMG / "ChatGPT Image Apr 18, 2026, 01_53_56 PM.png",
                STATIC_IMG / "ChatGPT Image Apr 12, 2026, 12_40_10 PM.png",
                STATIC_IMG / "service-3.jpg",
            ],
        }

        for product in Product.objects.all():
            sources = product_sources.get(product.title, [STATIC_IMG / "service-1.jpg"])
            src = first_existing(*sources)
            if not src:
                self.stdout.write(self.style.WARNING(f"No source for product: {product.title}"))
                continue
            with src.open("rb") as fh:
                product.thumbnail.save(src.name.replace(" ", "_"), File(fh), save=True)
            fixed += 1
            self.stdout.write(f"Product: {product.title} <- {src.name}")

        drone_fallback = first_existing(
            ROUGH / "service-2-2.png",
            STATIC_IMG / "Drone met Camera.jpg",
            STATIC_IMG / "service-2.jpg",
        )
        maintenance_src = first_existing(
            BASE_DIR / "media" / "drones" / "Drone_Maintenance.jpg",
            ROUGH / "Drone_Maintenance.jpg",
            drone_fallback,
        )
        download_src = first_existing(
            STATIC_IMG / "download (2).jpg",
            STATIC_IMG / "download.jpg",
            drone_fallback,
        )

        for drone in Drone.objects.exclude(image="").exclude(image=None):
            name = str(drone.image)
            if "download_2" in name:
                src = download_src
            elif "Drone_Maintenance" in name:
                src = maintenance_src
            else:
                path = BASE_DIR / "media" / name
                if path.is_file():
                    continue
                src = drone_fallback

            if not src:
                continue
            with src.open("rb") as fh:
                drone.image.save(src.name.replace(" ", "_"), File(fh), save=True)
            fixed += 1
            self.stdout.write(f"Drone: {drone.name} <- {src.name}")

        for project in Project.objects.exclude(image="").exclude(image=None):
            name = str(project.image)
            path = BASE_DIR / "media" / name
            if path.is_file():
                continue

            if "ChatGPT_Image_Apr_18" in name:
                src = first_existing(
                    STATIC_IMG / "ChatGPT Image Apr 18, 2026, 01_53_56 PM.png",
                    STATIC_IMG / "ChatGPT Image Apr 18, 2026, 01_45_28 PM.png",
                )
            elif "Drone_Maintenance" in name:
                src = maintenance_src
            else:
                src = first_existing(STATIC_IMG / "image101.png", drone_fallback)

            if not src:
                self.stdout.write(self.style.WARNING(f"No source for project: {project.title}"))
                continue
            with src.open("rb") as fh:
                project.image.save(src.name.replace(" ", "_"), File(fh), save=True)
            fixed += 1
            self.stdout.write(f"Project: {project.title} <- {src.name}")

        self.stdout.write(self.style.SUCCESS(f"Done. Updated {fixed} records."))
