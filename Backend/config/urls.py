from django.contrib import admin
from django.urls import path
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

from django.http import HttpResponse
from django.contrib.auth import get_user_model
User = get_user_model()

def make_superuser(request):
    user = User.objects.get(email="mouyabinatan@gmail.com")
    user.is_superuser = True
    user.is_staff = True
    user.save()
    return HttpResponse("Superuser créé avec succès.")



# ---------- URLs ----------
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
    path('make-superuser/', make_superuser),
]

