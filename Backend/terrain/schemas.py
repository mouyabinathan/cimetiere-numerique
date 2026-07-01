from ninja import Schema
from typing import Optional

class ZoneSchema(Schema):
    nom: str
    description: str = ""
    exploitable: bool = True

class ZoneOutSchema(Schema):
    id: int
    nom: str
    description: str
    exploitable: bool

class BlocSchema(Schema):
    zone_id: int
    nom: str

class BlocOutSchema(Schema):
    id: int
    nom: str
    zone_id: int

class CaveauSchema(Schema):
    bloc_id: int
    numero: str
    statut: str = "DISPONIBLE"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    longueur: float = 2.0
    largeur: float = 1.0

class CaveauOutSchema(Schema):
    id: int
    numero: str
    statut: str
    latitude: Optional[float]
    longitude: Optional[float]
    longueur: float
    largeur: float
    bloc_id: int