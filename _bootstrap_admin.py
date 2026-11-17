"""
Ensure the Django admin superuser exists, using environment variables.
Runs on every boot (render.yaml start command) so /admin/ always works.
Set DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_EMAIL / DJANGO_SUPERUSER_PASSWORD.
"""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_management.settings")
django.setup()

from django.contrib.auth.models import User

username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@sms-fake.local")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if not password:
    print("admin bootstrap skipped: DJANGO_SUPERUSER_PASSWORD not set")
    raise SystemExit(0)

user, created = User.objects.get_or_create(
    username=username, defaults={"email": email}
)
user.is_staff = True
user.is_superuser = True
user.email = email
user.set_password(password)
user.save()
print(f"admin superuser ready: {username} ({'created' if created else 'updated'})")
