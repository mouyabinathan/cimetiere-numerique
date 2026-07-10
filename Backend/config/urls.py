from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ninja import NinjaAPI
from users.api import router as users_router
from terrain.api import router as terrain_router
from reservations.api import router as reservations_router
from facturation.api import router as facturation_router
from terrain.reporting import router as reporting_router

# ---------- API ----------
api = NinjaAPI(title="Gestion Cimetière API", version="1.0.0")
api.add_router("/users", users_router)
api.add_router("/terrain", terrain_router)
api.add_router("/reservations", reservations_router)
api.add_router("/facturation", facturation_router)
api.add_router("/reporting", reporting_router)

# ---------- URLs ----------
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]

# ---------- Servir les fichiers statiques (même en production) ----------
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)