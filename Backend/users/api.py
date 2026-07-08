from ninja import Router
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random
import threading
from users.schemas import RegisterSchema, LoginSchema, MFAVerifySchema   
from users.auth import AuthBearer, AdminOnly
from users.schemas import UserOutSchema
from typing import List


User = get_user_model()
router = Router()

@router.post("/register")
def register(request, data: RegisterSchema):
    # Générer username automatiquement si pas fourni
    username = data.username or data.email.split("@")[0]
    if User.objects.filter(email=data.email).exists():
        return {"error": "Email déjà utilisé"}
    if User.objects.filter(username=username).exists():
        username = f"{username}_{User.objects.count()}"
    user = User.objects.create_user(
        username=username,
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
        telephone=data.telephone,
        role=data.role
    )
    return {"message": "Compte créé avec succès", "id": user.id}

@router.post("/login")
def login(request, data: LoginSchema):
    try:
        user = User.objects.get(email=data.email)
    except User.DoesNotExist:
        return {"error": "Utilisateur introuvable"}
    if not user.check_password(data.password):
        return {"error": "Mot de passe incorrect"}
    
    # ✅ MFA réactivé avec envoi asynchrone
    code = str(random.randint(100000, 999999))
    user.mfa_code = code
    user.mfa_expires_at = timezone.now() + timedelta(minutes=10)
    user.save()
    
    # ✅ Envoi de l'email en arrière-plan (ne bloque pas la réponse)
    def send_email_async():
        try:
            from users.email import envoyer_code_mfa
            envoyer_code_mfa(user.email, code)
        except Exception as ex:
            print(f">>> Echec envoi email : {ex}")
    
    thread = threading.Thread(target=send_email_async)
    thread.start()
    
    # ✅ Réponse immédiate (sans attendre l'email)
    return {"message": "Code MFA envoyé"}
    
@router.post("/verify-mfa")
def verify_mfa(request, data: MFAVerifySchema):
    try:
        user = User.objects.get(email=data.email)
    except User.DoesNotExist:
        return {"error": "Utilisateur introuvable"}
    if user.mfa_code != data.code:
        return {"error": "Code incorrect"}
    if timezone.now() > user.mfa_expires_at:
        return {"error": "Code expiré"}
    user.mfa_code = ""
    user.save()
    from users.auth import generer_token
    token = generer_token(user)
    return {
        "message": "Connexion réussie",
        "role": user.role,
        "token": token,
        "email": user.email,
        "nom": f"{user.first_name} {user.last_name}".strip() or user.username,
    }

    
@router.get("/list", response=List[UserOutSchema], auth=AdminOnly())
def list_users(request):
    return User.objects.all().order_by("-date_joined")

@router.post("/create", response=UserOutSchema, auth=AdminOnly())
def create_user(request, data: RegisterSchema):
    # Générer username depuis email si non fourni
    username = data.username.strip() if data.username else data.email.split("@")[0].lower().replace(".", "_")
    
    # Éviter les doublons de username
    base_username = username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}_{counter}"
        counter += 1

    if User.objects.filter(email=data.email).exists():
        return {"error": "Email déjà utilisé"}

    user = User.objects.create_user(
        username=username,
        email=data.email,
        password=data.password,
        first_name=data.first_name if hasattr(data, 'first_name') else "",
        last_name=data.last_name if hasattr(data, 'last_name') else "",
        telephone=data.telephone,
        role=data.role
    )
    return user