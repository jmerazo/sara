import json
from .firebase import cred
from firebase_admin import auth
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import Users

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@csrf_exempt
def firebase_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        token = data.get('token')

        try:
            # Verificar el token de Firebase
            decoded_token = auth.verify_id_token(token)
            email = decoded_token.get('email')  # Obtén el correo del token decodificado
            user_data_from_google = {
                'given_name': decoded_token.get('given_name', ''),
                'family_name': decoded_token.get('family_name', ''),
                'email': decoded_token.get('email', ''),
                'picture': decoded_token.get('picture', ''),
                'locale': decoded_token.get('locale', ''),
            }

            # Verificar el usuario en la base de datos local
            user = Users.objects.filter(email=email).first()
            if not user:
                return JsonResponse({'error': 'User does not exist'}, status=404)

            # Generar tokens locales
            tokens = get_tokens_for_user(user)

            # Preparar el user_data para devolver
            user_data = {
                'id': user.id,
                'role': user.role,
                'email': user.email,
                'document_type': user.document_type,
                'document_number': user.document_number,
                'cellphone': user.cellphone,
                'entity': user.entity,
                'profession': user.profession,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'state': user.state,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'given_name': user_data_from_google.get('given_name', ''),
                'family_name': user_data_from_google.get('family_name', ''),
                'email': user_data_from_google.get('email', ''),
                'picture': user_data_from_google.get('picture', ''),
                'locale': user_data_from_google.get('locale', '')
            }

            new_response = JsonResponse({
                'success': 'Tokens set',
                'access': tokens['access'],
                'refresh': tokens['refresh'],
                'user_data': user_data,
                'status': 'success'
            });

            # Configura las cookies (opcional, dependiendo de tu enfoque de autenticación)
            new_response.set_cookie(
                'access_token', tokens['access'], httponly=True, 
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
            )

            if 'REFRESH_TOKEN_LIFETIME' in settings.SIMPLE_JWT:
                max_age = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
            else:
                max_age = 3600  # Un valor por defecto, por ejemplo, 1 hora.

            new_response.set_cookie(
                'refresh_token', tokens['refresh'], httponly=True, max_age=max_age
            )

            return new_response

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=401)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)