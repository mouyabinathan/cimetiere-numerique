import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email="admin@cimetiere.com").exists():
    User.objects.create_superuser(
        username="admin",
        email="mouyabinathan@gmail.com",
        password="Admin123456",
        first_name="Admin",
        last_name="Principal",
        role="ADMIN"
    )
    print("Super-utilisateur créé.")
else:
    print("Existe déjà.")