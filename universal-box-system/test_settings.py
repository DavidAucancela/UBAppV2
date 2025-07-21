#!/usr/bin/env python
import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Import Django and setup
import django
django.setup()

from django.conf import settings

print("INSTALLED_APPS:")
for app in settings.INSTALLED_APPS:
    print(f"  - {app}")

print("\nCustom User Model:", getattr(settings, 'AUTH_USER_MODEL', 'Not set'))
print("REST Framework configured:", 'REST_FRAMEWORK' in dir(settings))