import jwt
import os
from django.conf import settings
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.utils.dateformat import format
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

load_dotenv()

def verify_jwt(token):
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=[os.getenv('ALGORITHM')])
        return payload
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

def generate_jwt(id):
    token = jwt.encode(
        {'id': id}, 
        os.getenv('JWT_SECRET'), 
        algorithm=os.getenv('ALGORITHM')
    )
    return token

def formatter_date(date):
    return format(localtime(date), 'j F Y', use_l10n=True, locale='es')