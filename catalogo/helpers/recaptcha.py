import requests
from django.conf import settings
import os

def verify_recaptcha(recaptcha_response):
    secret_key = os.getenv('RECAPTCHA_PRIVATE_KEY')

    if secret_key is None:
        raise Exception("La clave secreta de reCAPTCHA no está configurada en settings.py")

    # Envía una solicitud POST al servidor de reCAPTCHA para verificar el token
    response = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
        'secret': secret_key,
        'response': recaptcha_response
    })

    # Analiza la respuesta JSON del servidor de reCAPTCHA
    resultado = response.json()

    # Verifica si la respuesta del servidor indica que el reCAPTCHA es válido
    if resultado['success']:
        return True
    else:
        return False