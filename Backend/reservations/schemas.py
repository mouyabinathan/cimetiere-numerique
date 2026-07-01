from ninja import Schema
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class ReservationSchema(Schema):
    caveau_id: int
    nom_defunt: str
    prenom_defunt: str
    date_deces: date
    notes: str = ""

class ReservationOutSchema(Schema):
    id: int
    client_id: int
    caveau_id: int
    statut: str
    nom_defunt: str
    prenom_defunt: str
    date_deces: date
    date_demande: datetime
    date_validation: Optional[datetime]
    notes: str

class ValidationSchema(Schema):
    statut: str  
    


class ConcessionSchema(Schema):
    reservation_id: int
    type_concession: str = "TEMPORAIRE"
    date_debut: date
    duree_annees: int = 10
    montant: Decimal

class ConcessionOutSchema(Schema):
    id: int
    reservation_id: int
    type_concession: str
    statut: str
    date_debut: date
    date_fin: Optional[date]
    duree_annees: int
    montant: Decimal

class ExhumationSchema(Schema):
    reservation_id: int
    motif: str
    date_exhumation: Optional[date] = None

class ExhumationOutSchema(Schema):
    id: int
    reservation_id: int
    demandeur_id: int
    statut: str
    motif: str
    date_demande: datetime
    date_validation: Optional[datetime]
    date_exhumation: Optional[date]
    notes_admin: str

class ExhumationValidationSchema(Schema):
    statut: str
    notes_admin: str = ""
    date_exhumation: Optional[date] = None    