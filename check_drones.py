#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dpramp_project.settings')
django.setup()

from notes.models import Drone

print('=== Drone Database Check ===')
print(f'Total drones in database: {Drone.objects.count()}')
print(f'Active drones: {Drone.objects.filter(active=True).count()}')
print(f'Featured drones: {Drone.objects.filter(featured=True, active=True).count()}')

print('\n=== All Drones ===')
for drone in Drone.objects.all():
    print(f'- {drone.name}')
    print(f'  Active: {drone.active}')
    print(f'  Featured: {drone.featured}')
    print(f'  Price: {drone.price}')
    print(f'  Slug: {drone.slug}')
    print(f'  Has image: {bool(drone.image)}')
    print()

print('=== Active Drones for Shop ===')
active_drones = Drone.objects.filter(active=True).order_by("-featured", "-created_at")
for drone in active_drones:
    print(f'- {drone.name} (Featured: {drone.featured})')
