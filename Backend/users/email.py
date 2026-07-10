from django.core.mail import send_mail, EmailMessage
from django.conf import settings

def envoyer_code_mfa(email, code):
    print(f">>> ENVOI EMAIL à {email} avec code {code}")
    send_mail(
        subject="Votre code de connexion - CimétièrePRO",
        message=f"Votre code de vérification est : {code}\n\nCe code expire dans 10 minutes.\n\nCimetière Municipal de Pointe-Noire",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
    print(f">>> EMAIL ENVOYÉ à {email}")

def envoyer_confirmation_reservation(email, nom_defunt, numero_caveau):
    send_mail(
        subject="Confirmation de votre réservation",
        message=f"Votre réservation a été enregistrée.\n\nDéfunt : {nom_defunt}\nCaveau : {numero_caveau}\nStatut : En attente de validation\n\nCimetière Municipal de Pointe-Noire",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

def envoyer_facture_email(email, numero_facture, pdf_buffer):
    msg = EmailMessage(
        subject=f"Votre facture {numero_facture}",
        body=f"Veuillez trouver ci-joint votre facture {numero_facture}.\n\nCimetière Municipal de Pointe-Noire",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    msg.attach(f"facture_{numero_facture}.pdf", pdf_buffer.read(), "application/pdf")
    msg.send(fail_silently=False)