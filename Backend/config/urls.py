from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from users.api import router as users_router
from terrain.api import router as terrain_router
from reservations.api import router as reservations_router
from facturation.api import router as facturation_router
from terrain.reporting import router as reporting_router
from django.http import HttpResponse
import subprocess

# ---------- API ----------
api = NinjaAPI(title="Gestion Cimetière API", version="1.0.0")
api.add_router("/users", users_router)
api.add_router("/terrain", terrain_router)
api.add_router("/reservations", reservations_router)
api.add_router("/facturation", facturation_router)
api.add_router("/reporting", reporting_router)

# ---------- Création superuser ----------
def create_superuser(request):
    try:
        result = subprocess.run(
            ['python', 'Backend/create_superuser.py'],
            capture_output=True,
            text=True,
            cwd='.'  # Ajoute ce paramètre pour être sûr du chemin
        )
        return HttpResponse(result.stdout + result.stderr, content_type="text/plain")
    except Exception as e:
        return HttpResponse(f"Erreur: {e}", status=500)

# ---------- URLs ----------
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
    path('create-superuser/', create_superuser),
]