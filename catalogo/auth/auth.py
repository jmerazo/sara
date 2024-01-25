from rest_framework import viewsets
from django.conf import settings
from .models import Users
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
import random,string
from django.http import JsonResponse

def generate_random_id(length):
            characters = string.ascii_letters + string.digits
            random_id = ''.join(random.choice(characters) for _ in range(length))
            return random_id

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data['access']
            refresh_token = response.data['refresh']

            # Decodifica el token para obtener el user_id
            token = AccessToken(access_token)
            user_id = token['user_id']

            user_data = {}
            try:
                user_instance = Users.objects.get(id=user_id)  # Obtén la instancia del usuario
                # Construye el user_data aquí...
                user_data = {
                    'rol': user_instance.rol,
                    'email': user_instance.email,
                    'document_type': user_instance.document_type,
                    'document_number': user_instance.document_number,
                    'cellphone': user_instance.cellphone,
                    'entity': user_instance.entity,
                    'profession': user_instance.profession,
                    'first_name': user_instance.first_name,
                    'last_name': user_instance.last_name,
                    'state': user_instance.state,
                    'is_staff': user_instance.is_staff,
                    'is_superuser': user_instance.is_superuser
                }
            except Users.DoesNotExist:
                pass  # Maneja el caso en que el usuario no existe

            # Construye la respuesta con tokens y datos del usuario
            new_response = JsonResponse({
                'success': 'Tokens set',
                'access': access_token,  # Incluye el token de acceso
                'refresh': refresh_token,  # Incluye el token de actualización
                'user_data': user_data  # Incluye los datos del usuario
            })

            # Configura las cookies (opcional, dependiendo de tu enfoque de autenticación)
            new_response.set_cookie(
                'access_token', access_token, httponly=True, 
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
            )
            new_response.set_cookie(
                'refresh_token', refresh_token, httponly=True, 
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
            )

            return new_response
        else:
            return response  # Devuelve la respuesta original si el status code no es 200

class CurrentUser(viewsets.ModelViewSet):
     def get_queryset(self):
      user = self.request.user 
      return self.serializer_class.Meta.model.objects.filter(usuario=user)