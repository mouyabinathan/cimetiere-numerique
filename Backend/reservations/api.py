from ninja import Router
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import get_user_model
from reservations.models import Reservation, Concession
from reservations.schemas import ReservationSchema, ReservationOutSchema, ValidationSchema, ConcessionSchema, ConcessionOutSchema
from terrain.models import Caveau
from users.auth import AuthBearer, AdminOnly, AdminOrSecretariat
from typing import List

User = get_user_model()
router = Router()

@router.post("/", response=ReservationOutSchema, auth=AuthBearer())
def create_reservation(request, data: ReservationSchema):
    client = request.auth
    caveau = get_object_or_404(Caveau, id=data.caveau_id)
    if caveau.statut != "DISPONIBLE":
        return {"error": "Ce caveau n'est pas disponible"}
    reservation = Reservation.objects.create(
        client=client,
        caveau=caveau,
        nom_defunt=data.nom_defunt,
        prenom_defunt=data.prenom_defunt,
        date_deces=data.date_deces,
        notes=data.notes
    )
    caveau.statut = "RESERVE"
    caveau.save()
    from users.email import envoyer_confirmation_reservation
    envoyer_confirmation_reservation(
        client.email,
        f"{data.prenom_defunt} {data.nom_defunt}",
        caveau.numero
    )
    return reservation

@router.get("/", response=List[ReservationOutSchema], auth=AuthBearer())
def list_reservations(request):
    user = request.auth
    # Admin et secrétariat voient tout
    if user.role in ("ADMIN", "SECRETARIAT", "AGENT"):
        return Reservation.objects.all()
    # Client voit uniquement ses propres réservations
    return Reservation.objects.filter(client=user)
    
@router.get("/{reservation_id}", response=ReservationOutSchema, auth=AuthBearer())
def get_reservation(request, reservation_id: int):
    return get_object_or_404(Reservation, id=reservation_id)

@router.put("/{reservation_id}/valider", response=ReservationOutSchema, auth=AdminOrSecretariat())
def valider_reservation(request, reservation_id: int, data: ValidationSchema):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    reservation.statut = data.statut
    reservation.date_validation = timezone.now()
    if data.statut == "VALIDEE":
        reservation.caveau.statut = "OCCUPE"
        reservation.caveau.save()
    elif data.statut == "REFUSEE":
        reservation.caveau.statut = "DISPONIBLE"
        reservation.caveau.save()
    reservation.save()
    return reservation

@router.post("/concessions/create", response=ConcessionOutSchema, auth=AdminOrSecretariat())
def create_concession(request, data: ConcessionSchema):
    reservation = get_object_or_404(Reservation, id=data.reservation_id)
    if data.type_concession == "PERPETUELLE":
        date_fin = None
    else:
        date_fin = data.date_debut.replace(year=data.date_debut.year + data.duree_annees)
    concession = Concession.objects.create(
        reservation=reservation,
        type_concession=data.type_concession,
        date_debut=data.date_debut,
        date_fin=date_fin,
        duree_annees=data.duree_annees,
        montant=data.montant
    )
    return concession

@router.get("/concessions/list", response=List[ConcessionOutSchema], auth=AdminOrSecretariat())
def list_concessions(request):
    return Concession.objects.all()

@router.get("/concessions/{concession_id}", response=ConcessionOutSchema, auth=AuthBearer())
def get_concession(request, concession_id: int):
    return get_object_or_404(Concession, id=concession_id)

@router.put("/concessions/{concession_id}/resilier", response=ConcessionOutSchema, auth=AdminOnly())
def resilier_concession(request, concession_id: int):
    concession = get_object_or_404(Concession, id=concession_id)
    concession.statut = "RESILIEE"
    concession.save()
    concession.reservation.caveau.statut = "DISPONIBLE"
    concession.reservation.caveau.save()
    return concession

from reservations.models import Exhumation
from reservations.schemas import ExhumationSchema, ExhumationOutSchema, ExhumationValidationSchema

@router.post("/exhumations/create", response=ExhumationOutSchema, auth=AuthBearer())
def create_exhumation(request, data: ExhumationSchema):
    demandeur = request.auth
    reservation = get_object_or_404(Reservation, id=data.reservation_id)
    exhumation = Exhumation.objects.create(
        reservation=reservation,
        demandeur=demandeur,
        motif=data.motif,
        date_exhumation=data.date_exhumation
    )
    return exhumation

@router.get("/exhumations/list", response=List[ExhumationOutSchema], auth=AdminOrSecretariat())
def list_exhumations(request):
    return Exhumation.objects.all()

@router.get("/exhumations/{exhumation_id}", response=ExhumationOutSchema, auth=AuthBearer())
def get_exhumation(request, exhumation_id: int):
    return get_object_or_404(Exhumation, id=exhumation_id)

@router.put("/exhumations/{exhumation_id}/valider", response=ExhumationOutSchema, auth=AdminOnly())
def valider_exhumation(request, exhumation_id: int, data: ExhumationValidationSchema):
    exhumation = get_object_or_404(Exhumation, id=exhumation_id)
    exhumation.statut = data.statut
    exhumation.notes_admin = data.notes_admin
    exhumation.date_validation = timezone.now()
    if data.date_exhumation:
        exhumation.date_exhumation = data.date_exhumation
    if data.statut == "EFFECTUEE":
        exhumation.reservation.caveau.statut = "DISPONIBLE"
        exhumation.reservation.caveau.save()
    exhumation.save()
    return exhumation