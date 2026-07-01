from django.contrib import admin
from .models import Reservation, Concession, Exhumation

admin.site.register(Reservation)
admin.site.register(Concession)
admin.site.register(Exhumation)         