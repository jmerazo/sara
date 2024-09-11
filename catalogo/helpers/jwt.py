import jwt
import os
import json
from django.conf import settings
from datetime import datetime, timedelta
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _
from django.utils.dateformat import format
from django.utils.timezone import localtime
from dotenv import load_dotenv

from ..models import Users
from ..users.serializers import UsersSerializer

load_dotenv()

def verify_jwt(token):
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=[os.getenv('ALGORITHM')])
        user = Users.objects.filter(email=payload['id']).first()
        if user and user.token == token:
            return payload
        return None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def validate_object_id(id, res):
    try:
        int_id = int(id)
    except ValueError:
        return res.status(400).json({'msg': _("El id no es válido")})

def handle_not_found_error(msg_error, res):
    return res.status(404).json({'msg': msg_error})

def unique_id():
    return format(localtime(), 'U') + format(datetime.now(), 'YmdHis')

def generate_jwt(user_id):
    payload = {
        'id': user_id,
        'exp': datetime.utcnow() + timedelta(minutes=30),  # Token de acceso expira en 30 minutos
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm=os.getenv('ALGORITHM'))
    return token.decode('utf-8')  # Convertir el token a string

def generate_jwt_register(user_id):
    payload = {
        'id': user_id,
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm=os.getenv('ALGORITHM'))
    return token.decode('utf-8')  # Convertir el token a string

def formatter_date(date):
    return format(localtime(date), 'j F Y', use_l10n=True, locale='es')

@csrf_exempt
@require_http_methods(["POST"])
def verify_token(request):
    try:
        data = json.loads(request.body)
        token = data.get('token')

        if not token:
            return JsonResponse({'isValid': False, 'error': _('No se proporcionó token')}, status=400)

        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=[os.getenv('ALGORITHM')])
        
        # Verificar si el usuario existe y está activo
        try:
            user = Users.objects.get(id=payload['id'])
            if not user.is_active:
                return JsonResponse({'isValid': False, 'error': _('Usuario no activo')}, status=401)
        except Users.DoesNotExist:
            return JsonResponse({'isValid': False, 'error': _('Usuario no encontrado')}, status=404)

        # Serializar los datos del usuario
        user_data = UsersSerializer(user).data

        return JsonResponse({
            'isValid': True, 
            'userId': payload['id'],
            'userData': user_data
        })

    except jwt.ExpiredSignatureError:
        return JsonResponse({'isValid': False, 'error': _('El token ha expirado')}, status=401)

    except jwt.InvalidTokenError:
        return JsonResponse({'isValid': False, 'error': _('Token inválido')}, status=401)

    except Exception as e:
        return JsonResponse({'isValid': False, 'error': str(e)}, status=400)
    
def generate_refresh_token(id):
    payload = {
        'id': id,
        'exp': datetime.utcnow() + timedelta(days=7),  # Token de actualización expira en 7 días
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm=os.getenv('ALGORITHM'))