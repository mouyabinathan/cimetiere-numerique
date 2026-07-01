from ninja import Schema
from typing import Optional
from datetime import datetime
from decimal import Decimal

class FactureOutSchema(Schema):
    id: int
    reservation_id: int
    numero: str
    montant: Decimal
    statut: str
    date_emission: datetime
    date_paiement: Optional[datetime]

class PaiementSchema(Schema):
    facture_id: int
    canal: str
    montant: Decimal
    reference: str = ""

class PaiementOutSchema(Schema):
    id: int
    facture_id: int
    canal: str
    montant: Decimal
    reference: str
    date: datetime