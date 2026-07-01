from django.db import models
from django.contrib.auth import get_user_model
from terrain.models import Caveau

User = get_user_model()

class Reservation(models.Model):

    class Statut(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        VALIDEE    = 'VALIDEE', 'Validée'
        REFUSEE    = 'REFUSEE', 'Refusée'
        ANNULEE    = 'ANNULEE', 'Annulée'

    client        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    caveau        = models.ForeignKey(Caveau, on_delete=models.CASCADE, related_name='reservations')
    statut        = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    nom_defunt    = models.CharField(max_length=100)
    prenom_defunt = models.CharField(max_length=100)
    date_deces    = models.DateField()
    date_demande  = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    notes         = models.TextField(blank=True)

    def __str__(self):
        return f"Réservation {self.id} - {self.nom_defunt} ({self.statut})"


class Concession(models.Model):

    class Type(models.TextChoices):
        TEMPORAIRE  = 'TEMPORAIRE', 'Temporaire'
        PERPETUELLE = 'PERPETUELLE', 'Perpétuelle'

    class Statut(models.TextChoices):
        ACTIVE    = 'ACTIVE', 'Active'
        EXPIREE   = 'EXPIREE', 'Expirée'
        RESILIEE  = 'RESILIEE', 'Résiliée'

    reservation   = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='concession')
    type_concession = models.CharField(max_length=20, choices=Type.choices, default=Type.TEMPORAIRE)
    statut        = models.CharField(max_length=20, choices=Statut.choices, default=Statut.ACTIVE)
    date_debut    = models.DateField()
    date_fin      = models.DateField(null=True, blank=True)
    duree_annees  = models.IntegerField(default=10)
    montant       = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Concession {self.id} - {self.type_concession} ({self.statut})"    
    
class Exhumation(models.Model):

    class Statut(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        VALIDEE    = 'VALIDEE', 'Validée'
        REFUSEE    = 'REFUSEE', 'Refusée'
        EFFECTUEE  = 'EFFECTUEE', 'Effectuée'

    reservation      = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='exhumations')
    demandeur        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exhumations')
    statut           = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    motif            = models.TextField()
    date_demande     = models.DateTimeField(auto_now_add=True)
    date_validation  = models.DateTimeField(null=True, blank=True)
    date_exhumation  = models.DateField(null=True, blank=True)
    notes_admin      = models.TextField(blank=True)

    def __str__(self):
        return f"Exhumation {self.id} - {self.statut}"        