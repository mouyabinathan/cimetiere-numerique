from ninja import Router
from django.shortcuts import get_object_or_404
from terrain.models import Zone, Bloc, Caveau
from terrain.schemas import (
    ZoneSchema, ZoneOutSchema,
    BlocSchema, BlocOutSchema,
    CaveauSchema, CaveauOutSchema
)
from users.auth import AuthBearer, AdminOnly
from typing import List

router = Router()

# ---- ZONES ----
@router.post("/zones", response=ZoneOutSchema, auth=AdminOnly())
def create_zone(request, data: ZoneSchema):
    zone = Zone.objects.create(**data.dict())
    return zone

@router.get("/zones", response=List[ZoneOutSchema], auth=AuthBearer())
def list_zones(request):
    return Zone.objects.all()

# ---- BLOCS ----
@router.post("/blocs", response=BlocOutSchema, auth=AdminOnly())
def create_bloc(request, data: BlocSchema):
    zone = get_object_or_404(Zone, id=data.zone_id)
    bloc = Bloc.objects.create(zone=zone, nom=data.nom)
    return bloc

@router.get("/blocs", response=List[BlocOutSchema], auth=AuthBearer())
def list_blocs(request):
    return Bloc.objects.all()

# ---- CAVEAUX ----
@router.post("/caveaux", response=CaveauOutSchema, auth=AdminOnly())
def create_caveau(request, data: CaveauSchema):
    bloc = get_object_or_404(Bloc, id=data.bloc_id)
    caveau = Caveau.objects.create(
        bloc=bloc,
        numero=data.numero,
        statut=data.statut,
        latitude=data.latitude,
        longitude=data.longitude,
        longueur=data.longueur,
        largeur=data.largeur
    )
    return caveau

@router.get("/caveaux", response=List[CaveauOutSchema], auth=AuthBearer())
def list_caveaux(request):
    return Caveau.objects.all()

@router.get("/caveaux/{caveau_id}", response=CaveauOutSchema, auth=AuthBearer())
def get_caveau(request, caveau_id: int):
    return get_object_or_404(Caveau, id=caveau_id)

@router.get("/carte", response=List[CaveauOutSchema], auth=AuthBearer())
def get_carte(request):
    return Caveau.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    )

@router.get("/carte/stats", auth=AuthBearer())
def get_carte_stats(request):
    total = Caveau.objects.count()
    disponibles = Caveau.objects.filter(statut="DISPONIBLE").count()
    reserves = Caveau.objects.filter(statut="RESERVE").count()
    occupes = Caveau.objects.filter(statut="OCCUPE").count()
    inexploitables = Caveau.objects.filter(statut="INEXPLOITABLE").count()
    return {
        "total": total,
        "disponibles": disponibles,
        "reserves": reserves,
        "occupes": occupes,
        "inexploitables": inexploitables,
        "taux_occupation": round((occupes / total * 100), 2) if total > 0 else 0
    }