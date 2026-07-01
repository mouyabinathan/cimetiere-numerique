from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    
    class Role(models.TextChoices):
        ADMIN       = 'ADMIN', 'Administrateur'
        AGENT       = 'AGENT', 'Agent de terrain'
        SECRETARIAT = 'SECRETARIAT', 'Secrétariat'
        CLIENT      = 'CLIENT', 'Client'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT
    )
    telephone = models.CharField(max_length=20, blank=True)
    mfa_code = models.CharField(max_length=6, blank=True)
    mfa_expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"