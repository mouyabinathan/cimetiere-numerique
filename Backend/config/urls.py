from django.contrib import admin
from django.urls import path, re_path
from ninja import NinjaAPI
from users.api import router as users_router
from terrain.api import router as terrain_router
from reservations.api import router as reservations_router
from facturation.api import router as facturation_router
from terrain.reporting import router as reporting_router
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import os
import requests

# ---------- API ----------
api = NinjaAPI(title="Gestion Cimetière API", version="1.0.0")
api.add_router("/users", users_router)
api.add_router("/terrain", terrain_router)
api.add_router("/reservations", reservations_router)
api.add_router("/facturation", facturation_router)
api.add_router("/reporting", reporting_router)

# ---------- Frontend Flet ----------
flet_started = False

@csrf_exempt
def flet_app(request, path=''):
    """Sert le frontend Flet"""
    global flet_started
    try:
        # Lance Flet en arrière-plan (une seule fois)
        if not flet_started:
            subprocess.Popen(
                ['python', 'frontend/main.py'],
                cwd=os.path.dirname(os.path.dirname(__file__)),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            flet_started = True
        
        # Redirige vers le port de Flet
        port = 8501
        if path:
            resp = requests.get(f'http://localhost:{port}/{path}')
        else:
            resp = requests.get(f'http://localhost:{port}/')
        return HttpResponse(resp.content, status=resp.status_code)
    except Exception as e:
        return HttpResponse(f"Erreur: {e}", status=500)

# ---------- URLs ----------
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
    re_path(r'^(?P<path>.*)$', flet_app),  # Sert le frontend pour toutes les autres URLs
]