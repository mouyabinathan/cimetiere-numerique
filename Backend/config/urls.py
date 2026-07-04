from django.contrib import admin
from django.urls import path, re_path
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ninja import NinjaAPI
from users.api import router as users_router
from terrain.api import router as terrain_router
from reservations.api import router as reservations_router
from facturation.api import router as facturation_router
from terrain.reporting import router as reporting_router
import subprocess
import os
import requests
import time

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
def serve_flet(request, path=''):
    global flet_started
    try:
        if not flet_started:
            subprocess.Popen(
                ['python', 'frontend/main.py'],
                cwd=os.path.dirname(os.path.dirname(__file__)),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            flet_started = True
            time.sleep(2)
        
        port = 8501
        url = f'http://localhost:{port}/{path}' if path else f'http://localhost:{port}/'
        resp = requests.get(url, timeout=10)
        return HttpResponse(resp.content, status=resp.status_code)
    except Exception as e:
        return HttpResponse(f"Erreur: {e}", status=500)

# ---------- URLs ----------
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
    re_path(r'^(?P<path>.*)$', serve_flet),
]