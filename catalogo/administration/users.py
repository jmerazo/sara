from rest_framework.response import Response
from django.contrib.auth.models import BaseUserManager
from rest_framework import status
from django.http import Http404
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from django.db.models import Q, Count
from decimal import Decimal
from ..models import CustomUser
from django.contrib.auth.models import User
from ..serializers import UsersSerializer
import random
import string
from django.utils import timezone
from ..helpers.recaptcha import verify_recaptcha
from ..managers import CustomUserManager

from django.shortcuts import render
#from captcha.fields import ReCaptchaField

from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

def generate_random_id(length):
            characters = string.ascii_letters + string.digits
            random_id = ''.join(random.choice(characters) for _ in range(length))
            return random_id

class UsersView(APIView):
    def get_object(self, pk=None):
        if pk is not None:
            try:
                return Users.objects.get(pk=pk)
            except Users.DoesNotExist:
                raise Http404
        else:
            return Users.objects.all()

    def get(self, request, pk=None, format=None):
        users = self.get_object(pk)
        
        if isinstance(users, Users):
            serializer = UsersSerializer(users)
        else:
            serializer = UsersSerializer(users, many=True)
            
        return Response(serializer.data)
    
    def post(self, request, format=None):
        adjusted_data = request.data.copy()
        
        existing_user = User.objects.filter(Q(email=adjusted_data['email']) | Q(document_number=adjusted_data['document_number'])).first()
        if existing_user:
            return Response({'error': f'El usuario ya está registrado con el correo electrónico {existing_user.email} y número de documento {existing_user.document_number}.'}, status=status.HTTP_400_BAD_REQUEST)

        user_fields = ['email', 'password', 'username', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active', 'last_login', 'date_joined']
        user_data = {key: adjusted_data[key] for key in user_fields if key in adjusted_data}

        custom_user_fields = ['document_type', 'document_number', 'rol', 'entity', 'cellphone', 'department', 'city', 'device', 'serial', 'profession', 'reason', 'state']
        custom_user_data = {key: adjusted_data[key] for key in custom_user_fields if key in adjusted_data}

        password = adjusted_data.pop('password', None)  # Obtener y quitar la contraseña del diccionario
        
        user = User.objects.create(**user_data)  # Crear el usuario en la base de datos
        user.set_password(password)
        user.save()  # Guardar el usuario en la base de datos

        custom_user = CustomUser.objects.create(user=user, **custom_user_data)  # Asociar con CustomUser

        serializer = UsersSerializer(custom_user)  # Actualizar el serializer con los datos del usuario
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UsersSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)