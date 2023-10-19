from rest_framework.response import Response
from django.db import connection, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.http import Http404
from rest_framework.views import APIView
from django.db.models import Q, F
from ..models import Users, Departments
from ..serializers import UsersSerializer
import random
import string
from django.utils import timezone
from django.contrib.auth.models import Group, Permission
from ..helpers.recaptcha import verify_recaptcha

from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

def generate_random_id(length):
            characters = string.ascii_letters + string.digits
            random_id = ''.join(random.choice(characters) for _ in range(length))
            return random_id

class UsersView(APIView):
    def get_queryset(self):
        # Consulta SQL directa
        query = """
            SELECT u.id, u.email, u.first_name, u.last_name, u.rol, u.is_active, u.document_type, u.document_number, u.entity, u.cellphone, u.department, d.name, u.city, u.device_movile, u.serial_device, u.profession, u.reason, u.state, u.is_staff, u.last_login, u.is_superuser, u.date_joined
            FROM Users AS u
            INNER JOIN departments AS d ON u.department = d.code
        """
        # Ejecutar la consulta
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        columns = ['id', 'email', 'first_name', 'last_name', 'rol', 'is_active', 'document_type', 'document_number', 'entity', 'cellphone', 'department', 'name', 'city', 'device_movile', 'serial_device', 'profession', 'reason', 'state', 'is_staff', 'last_login', 'is_superuser', 'date_joined']
        queryset = [dict(zip(columns, row)) for row in result]

        return queryset

    def get_object(self, pk=None):
        queryset = self.get_queryset()

        if pk is not None:
            try:
                user = next(user for user in queryset if user['id'] == pk)
                return user
            except StopIteration:
                raise Http404
        else:
            return queryset

    def get(self, request, pk=None, format=None):
        users = self.get_object(pk)

        if isinstance(users, dict):
            # Convertir el resultado en una lista de diccionarios
            users = [users]

        return Response(users)
    
    @transaction.atomic
    def post(self, request, format=None):
        adjusted_data = request.data.copy()

        existing_user = Users.objects.filter(Q(email=adjusted_data['email']) | Q(document_number=adjusted_data['document_number'])).first()
        if existing_user:
            return Response({'error': f'El usuario ya está registrado con el correo electrónico {existing_user.email} y número de documento {existing_user.document_number}.'}, status=status.HTTP_400_BAD_REQUEST)

        random_id = generate_random_id(8)
        user_active = 0
        user_rol_default = "DEFAULT"
        
        adjusted_data['active'] = user_active
        adjusted_data['rol'] = user_rol_default
        password = adjusted_data['password']

        serializer = UsersSerializer(data=adjusted_data)
        if serializer.is_valid():
            user = Users(
                email=adjusted_data['email'],
                first_name=adjusted_data['first_name'],
                last_name=adjusted_data['last_name'],
                rol='DEFAULT',
                is_active=0,
                document_type=adjusted_data['document_type'],
                document_number=adjusted_data['document_number'],
                entity=adjusted_data['entity'],
                cellphone=adjusted_data['cellphone'],
                department=adjusted_data['department'],
                city=adjusted_data['city'],
                profession=adjusted_data['profession'],
                reason=adjusted_data['reason'],
                state='REVIEW',
                is_staff=0,
                last_login=None,
                is_superuser=0,
                date_joined=timezone.now()
            )
            user.set_password(password)
            """ user.save() """  # Guarda el usuario antes de asignarle el grupo

            default_group = Group.objects.get(name='DEFAULT')
            user.groups.add(default_group)

            default_permission = Permission.objects.get(codename='view_user')
            user.user_permissions.add(default_permission)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        print('pk: ', pk)
        user = get_object_or_404(Users, id=pk)
        adjusted_data = request.data
        """ print('data user: ', adjusted_data) """
        print('user: ', user)

        # Aquí puedes realizar las validaciones y actualizaciones necesarias.
        # Por ejemplo, para actualizar el email y el número de documento:
        email = adjusted_data.get('email')
        document_number = adjusted_data.get('document_number')
        first_name = adjusted_data.get('first_name')
        last_name = adjusted_data.get('last_name')
        rol = adjusted_data.get('rol')
        document_type = adjusted_data.get('document_type')
        entity = adjusted_data.get('entity')
        cellphone = adjusted_data.get('cellphone')
        department = adjusted_data.get('department')
        city = adjusted_data.get('city')
        profession = adjusted_data.get('profession')

        if 'is_active' in adjusted_data:
            is_active = adjusted_data['is_active']
            user.is_active = is_active
        
        # Asegurémonos de que el nuevo email o número de documento no existan en otros usuarios
        existing_user = Users.objects.exclude(id=pk).filter(Q(email=email) | Q(document_number=document_number)).first()
        if existing_user:
            return Response({'error': f'El correo electrónico {email} o número de documento {document_number} ya están registrados en otro usuario.'}, status=status.HTTP_400_BAD_REQUEST)

        # Actualizamos los campos del usuario
        user.email = email
        user.document_number = document_number
        user.first_name = first_name
        user.last_name = last_name
        user.rol = rol
        user.document_type = document_type
        user.entity = entity
        user.cellphone = cellphone
        user.department = department
        user.city = city
        user.profession = profession

        # Aquí debes continuar actualizando los demás campos según tus necesidades

        user.save()  # Guardar los cambios

        serializer = UsersSerializer(user)  # Serializa el usuario actualizado
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)