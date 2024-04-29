from rest_framework import viewsets
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from django.conf import settings
from ..models import Users
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
import random,string
from django.http import JsonResponse
import os, requests
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import urllib.parse

def generate_random_id(length):
            characters = string.ascii_letters + string.digits
            random_id = ''.join(random.choice(characters) for _ in range(length))
            return random_id

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super(CustomTokenObtainPairSerializer, self).__init__(*args, **kwargs)
        # Verificar si authType está presente y ajustar los campos necesarios
        auth_type = self.initial_data.get('authType', 'local')
        if auth_type == 'google':
            self.fields['email'].required = False
            self.fields['password'].required = False
        else:
            self.fields['email'].required = True
            self.fields['password'].required = True

    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False)
    code = serializers.CharField(required=False)

    def validate(self, attrs):
        auth_type = self.context.get('authType', 'local')
        print('Auth Type in serializer:', auth_type)
        if auth_type == 'google':
            code = attrs.get('code')
            if not code:
                raise serializers.ValidationError({"code": "Code is required for Google authentication."})
            return attrs
        else:
            email = attrs.get('email')
            password = attrs.get('password')
            if not email or not password:
                raise serializers.ValidationError({"email": "Email is required", "password": "Password is required"})
            return super().validate(attrs)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @csrf_exempt
    def post(self, request, *args, **kwargs):
         # Preparar los datos incluyendo explícitamente 'authType'
        data = request.data.copy()
        data['authType'] = data.get('authType', 'local')

        # Pasar explícitamente el 'authType' en el contexto del serializador
        context = self.get_serializer_context()
        context['authType'] = data['authType']

        serializer = self.get_serializer(data=data, context=context)
        print('data login: ', request.data)

        if serializer.is_valid():
            auth_type = data['authType']
            print('authType login: ', auth_type)
            if auth_type == 'google':
                print('i am here login google')
                return self.handle_google_auth(request, serializer.validated_data['code'])
            else:
                print('i am here local login')
                return self.handle_local_auth(request)
        else:
            print('Error serializer', serializer)
            return JsonResponse(serializer.errors, status=400)

    def handle_local_auth(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return self.enrich_response_with_user_data(response)
        return response

    def handle_google_auth(self, request, code):
        client_id = os.getenv('OAUTH2_KEY')
        client_secret = os.getenv('OAUTH2_SECRET')
        redirect_uri = os.getenv('OAUTH2_REDIRECT_URI')
        token_url = 'https://oauth2.googleapis.com/token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        # Codificar los datos manualmente
        encoded_data = urllib.parse.urlencode(data)
        print('i am here data: ', data)

        try:
            response = requests.post(token_url, headers=headers, data=encoded_data)
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data.get('access_token')

            # Aquí deberías obtener información del usuario desde Google, si necesario
            user_data = self.get_user_data_from_google(access_token)
            print('i am here user_data: ', user_data)
            return JsonResponse({
                'access': access_token,
                'user_data': user_data,
                'status': 'success'
            })

        except requests.exceptions.RequestException as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)  # Captura otros errores posibles

    def enrich_response_with_user_data(self, response):
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
                'id' : user_id,
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
        # Primero, determina el valor de max_age
        if 'REFRESH_TOKEN_LIFETIME' in settings.SIMPLE_JWT:
            max_age = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
        else:
            max_age = 3600  # Un valor por defecto, por ejemplo, 1 hora.

        # Luego, utiliza este valor en la llamada a set_cookie
        new_response.set_cookie(
            'refresh_token', refresh_token, httponly=True, max_age=max_age
        )

        return new_response

    def get_google_user_data(self, access_token):
        google_info_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
        response = requests.get(google_info_url, headers={'Authorization': f'Bearer {access_token}'})
        user_info = response.json()
        email = user_info.get('email')

        try:
            # Intenta buscar un usuario existente con el correo electrónico de Google
            user_instance = Users.objects.get(email=email)
            # Aquí puedes actualizar datos del usuario si es necesario
            user_data = {
                'id' : user_instance.id,
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
            return JsonResponse({'error': 'User does not exist'}, status=404)  # Devuelve una respuesta HTTP si no existe el usuario

        return {
            user_data
        }

class CurrentUser(viewsets.ModelViewSet):
     def get_queryset(self):
      user = self.request.user 
      return self.serializer_class.Meta.model.objects.filter(usuario=user)
     
class OAuth2Call(APIView):
    def post(self, request, *args, **kwargs):
        code = request.POST.get('code')
        client_id = os.getenv('OAUTH2_KEY')
        client_secret = os.getenv('OAUTH2_SECRET')
        redirect_uri = os.getenv('OAUTH2_REDIRECT_URI')
        token_url = 'https://oauth2.googleapis.com/token'
        
        data = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }

        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data.get('access_token')

            # Aquí deberías obtener información del usuario desde Google, si necesario
            user_data = self.get_user_data_from_google(access_token)

            return JsonResponse({
                'access': access_token,
                'user_data': user_data,
                'status': 'success'
            })

        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=400)
        
class CustomTokenObtainPair(TokenObtainPairView):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        auth_type = request.data.get('auth_type', 'local')
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
                print('users: ', user_instance)
                # Construye el user_data aquí...
                user_data = {
                    'id' : user_id,
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
            # Primero, determina el valor de max_age
            if 'REFRESH_TOKEN_LIFETIME' in settings.SIMPLE_JWT:
                max_age = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
            else:
                max_age = 3600  # Un valor por defecto, por ejemplo, 1 hora.

            # Luego, utiliza este valor en la llamada a set_cookie
            new_response.set_cookie(
                'refresh_token', refresh_token, httponly=True, max_age=max_age
            )
            
            return new_response
        else:
            return response  # Devuelve la respuesta original si el status code no es 200