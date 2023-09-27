from rest_framework.response import Response
from django.contrib.auth.models import BaseUserManager
from rest_framework import status
from django.http import Http404
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from django.db.models import Q, Count
from decimal import Decimal
from ..models import Users
from ..serializers import UsersSerializer
import random
import string
from ..helpers.recaptcha import verify_recaptcha
from ..managers import CustomUserManager

from django.shortcuts import render
#from captcha.fields import ReCaptchaField

from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

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

        custom_user_manager = CustomUserManager()
        
        existing_user = Users.objects.filter(Q(email=adjusted_data['email']) | Q(document_number=adjusted_data['document_number'])).first()
        if existing_user:
            return Response({'error': f'El usuario ya está registrado con el correo electrónico {existing_user.email} y número de documento {existing_user.document_number}.'}, status=status.HTTP_400_BAD_REQUEST)

        def generate_random_id(length):
            characters = string.ascii_letters + string.digits
            random_id = ''.join(random.choice(characters) for _ in range(length))
            return random_id

        random_id = generate_random_id(8)
        user_active = 0
        user_rol_default = "Básico"
        
        adjusted_data['id'] = random_id
        adjusted_data['active'] = user_active
        adjusted_data['rol'] = user_rol_default

        serializer = UsersSerializer(data=adjusted_data)
        if serializer.is_valid():
            user = custom_user_manager.create_user(email=adjusted_data['email'], password=None, **adjusted_data)
            serializer.save(user = user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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