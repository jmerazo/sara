import os
import jwt
import requests
from .firebase import cred
from dotenv import load_dotenv
from django.conf import settings
from rest_framework.views import APIView
from firebase_admin import auth as firebase_auth
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
load_dotenv()

from ..helpers.jwt import generate_jwt, generate_refresh_token, verify_token

class FirebaseLoginView(APIView):
    def post(self, request):
        firebase_token = request.data.get('token')
        if not firebase_token:
            return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_token = firebase_auth.verify_id_token(firebase_token)
            email = decoded_token.get('email')
            
            if not email:
                return Response({"error": "No email associated with this Firebase account"}, status=status.HTTP_400_BAD_REQUEST)
            
            User = get_user_model()
            user, created = User.objects.get_or_create(email=email)
            
            local_token = generate_jwt(user.id)

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
            }

            return Response({
                'token': local_token,
                'user_id': user.id,
                'user_data': user_data,
                'is_new_user': created
            })
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

# Añade una nueva vista para refrescar el token:
class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Refresh token not provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = verify_token(refresh_token)
            user_id = payload['user_id']
            new_access_token = generate_refresh_token(user_id)
            return Response({'access_token': new_access_token})
        except jwt.ExpiredSignatureError:
            return Response({"error": "Refresh token has expired"}, status=status.HTTP_403_FORBIDDEN)
        except jwt.InvalidTokenError:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_403_FORBIDDEN)
        
def verify_recaptcha(recaptcha_token):
    url = 'https://www.google.com/recaptcha/api/siteverify'
    data = {
        'secret': os.getenv('RECAPTCHA_PRIVATE_KEY'),
        'response': recaptcha_token
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        result = response.json()
        return result
    except requests.RequestException as e:
        return {'success': False, 'error': str(e)}

class AuthView(APIView):
    def post(self, request):
        firebase_token = request.data.get('token')
        recaptcha_token = request.data.get('recaptcha_token')

        if not firebase_token or not recaptcha_token:
            return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        recaptcha_result = verify_recaptcha(recaptcha_token)
        
        if not recaptcha_result['success']:
            error_codes = recaptcha_result.get('error-codes', [])
            error_message = f"reCAPTCHA verification failed: {', '.join(error_codes)}"
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_token = firebase_auth.verify_id_token(firebase_token)
            email = decoded_token.get('email')
            
            if not email:
                return Response({"error": "No email associated with this Firebase account"}, status=status.HTTP_400_BAD_REQUEST)
            
            User = get_user_model()
            user, created = User.objects.get_or_create(email=email)
            
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
            }

            return Response({
                'token': firebase_token,
                'user_id': user.id,
                'user_data': user_data,
                'is_new_user': created
            })
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)