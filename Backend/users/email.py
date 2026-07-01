from django.core.mail import send_mail, EmailMessage
from django.conf import settings

def envoyer_code_mfa(email, code):
    send_mail(
        subject="Votre code de connexion",
        message=f"""
Bonjour,

Votre code de vérification est : {code}

Ce code expire dans 10 minutes.

Cimetière Municipal de Pointe-Noire
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

def envoyer_confirmation_reservation(email, nom_defunt, numero_caveau):
    send_mail(
        subject="Confirmation de votre réservation",
        message=f"""
Bonjour,

Votre réservation a été enregistrée avec succès.

Défunt : {nom_defunt}
Caveau : {numero_caveau}
Statut : En attente de validation

Vous recevrez une confirmation dès validation par notre équipe.

Cimetière Municipal de Pointe-Noire
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

def envoyer_facture_email(email, numero_facture, pdf_buffer):
    msg = EmailMessage(
        subject=f"Votre facture {numero_facture}",
        body=f"""
Bonjour,

Veuillez trouver ci-joint votre facture {numero_facture}.

Merci de votre confiance.

Cimetière Municipal de Pointe-Noire
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    msg.attach(f"facture_{numero_facture}.pdf", pdf_buffer.read(), "application/pdf")
    msg.send(fail_silently=False)