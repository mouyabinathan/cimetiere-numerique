import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from ninja.security import HttpBearer
from datetime import datetime, timedelta, timezone

User = get_user_model()

SECRET_KEY = settings.SECRET_KEY

def generer_token(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.now(tz=timezone.utc) + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decoder_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        payload = decoder_token(token)
        if not payload:
            return None
        try:
            user = User.objects.get(id=payload['user_id'])
            return user
        except User.DoesNotExist:
            return None

class AdminOnly(HttpBearer):
    def authenticate(self, request, token):
        payload = decoder_token(token)
        if not payload:
            return None
        if payload['role'] != 'ADMIN':
            return None
        try:
            return User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            return None

class AdminOrSecretariat(HttpBearer):
    def authenticate(self, request, token):
        payload = decoder_token(token)
        if not payload:
            return None
        if payload['role'] not in ['ADMIN', 'SECRETARIAT']:
            return None
        try:
            return User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            return None