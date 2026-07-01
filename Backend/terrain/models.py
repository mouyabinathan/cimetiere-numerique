from django.db import models

class Zone(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    exploitable = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

class Bloc(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='blocs')
    nom = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.zone.nom} - {self.nom}"

class Caveau(models.Model):

    class Statut(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        RESERVE    = 'RESERVE', 'Réservé'
        OCCUPE     = 'OCCUPE', 'Occupé'
        INEXPLOITABLE = 'INEXPLOITABLE', 'Inexploitable'

    bloc       = models.ForeignKey(Bloc, on_delete=models.CASCADE, related_name='caveaux')
    numero     = models.CharField(max_length=20)
    statut     = models.CharField(max_length=20, choices=Statut.choices, default=Statut.DISPONIBLE)
    latitude   = models.FloatField(null=True, blank=True)
    longitude  = models.FloatField(null=True, blank=True)
    longueur   = models.FloatField(default=2.0)
    largeur    = models.FloatField(default=1.0)

    def __str__(self):
        return f"Caveau {self.numero} - {self.statut}"