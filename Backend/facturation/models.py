from django.db import models
from django.contrib.auth import get_user_model
from reservations.models import Reservation

User = get_user_model()

class Facture(models.Model):

    class Statut(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        PAYEE      = 'PAYEE', 'Payée'
        ANNULEE    = 'ANNULEE', 'Annulée'

    reservation   = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='facture')
    numero        = models.CharField(max_length=20, unique=True)
    montant       = models.DecimalField(max_digits=10, decimal_places=2)
    statut        = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    date_emission = models.DateTimeField(auto_now_add=True)
    date_paiement = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Facture {self.numero} - {self.statut}"

class Paiement(models.Model):

    class Canal(models.TextChoices):
        MTN      = 'MTN', 'MTN Mobile Money'
        AIRTEL   = 'AIRTEL', 'Airtel Money'
        ESPECES  = 'ESPECES', 'Espèces'
        VIREMENT = 'VIREMENT', 'Virement bancaire'

    facture    = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='paiements')
    canal      = models.CharField(max_length=20, choices=Canal.choices)
    montant    = models.DecimalField(max_digits=10, decimal_places=2)
    reference  = models.CharField(max_length=50, blank=True)
    date       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paiement {self.id} - {self.canal} - {self.montant}"