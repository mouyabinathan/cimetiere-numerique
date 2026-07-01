from ninja import Router
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import FileResponse
from facturation.models import Facture, Paiement
from facturation.schemas import FactureOutSchema, PaiementSchema, PaiementOutSchema
from facturation.pdf import generer_facture_pdf
from reservations.models import Reservation
from users.auth import AuthBearer, AdminOnly, AdminOrSecretariat
from typing import List
import random

router = Router()

def generer_numero_facture():
    return f"FACT-{timezone.now().year}-{random.randint(1000, 9999)}"

@router.post("/factures", response=FactureOutSchema, auth=AdminOrSecretariat())
def create_facture(request, reservation_id: int, montant: float):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    facture = Facture.objects.create(
        reservation=reservation,
        numero=generer_numero_facture(),
        montant=montant
    )
    return facture

@router.get("/factures", response=List[FactureOutSchema], auth=AdminOrSecretariat())
def list_factures(request):
    return Facture.objects.all()

@router.get("/factures/{facture_id}", response=FactureOutSchema, auth=AuthBearer())
def get_facture(request, facture_id: int):
    return get_object_or_404(Facture, id=facture_id)

@router.post("/paiements", response=PaiementOutSchema, auth=AdminOrSecretariat())
def create_paiement(request, data: PaiementSchema):
    facture = get_object_or_404(Facture, id=data.facture_id)
    paiement = Paiement.objects.create(
        facture=facture,
        canal=data.canal,
        montant=data.montant,
        reference=data.reference
    )
    facture.statut = "PAYEE"
    facture.date_paiement = timezone.now()
    facture.save()

    # ✅ Envoi automatique de la facture PDF par email
    try:
        from facturation.pdf import generer_facture_pdf
        from users.email import envoyer_facture_email

        pdf_buffer = generer_facture_pdf(facture)
        email_client = facture.reservation.client.email
        envoyer_facture_email(email_client, facture.numero, pdf_buffer)
    except Exception as ex:
        print(f">>> Echec envoi facture email : {ex}")

    return paiement


@router.get("/factures/{facture_id}/pdf", auth=AuthBearer())
def telecharger_facture_pdf(request, facture_id: int):
    facture = get_object_or_404(Facture, id=facture_id)
    buffer = generer_facture_pdf(facture)
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f"facture_{facture.numero}.pdf"
    )