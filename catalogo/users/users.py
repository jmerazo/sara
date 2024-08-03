from rest_framework.response import Response
from django.db import transaction
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.http import Http404
from rest_framework.views import APIView
from django.db.models import Q
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail

from .serializers import UsersCreateSerializer, UsersSerializer
from ..utils.serializers import RolSerializer
from .models import UserModules
from ..utils.models import Rol
from ..page.models import Pages
from ..models import Users
from ..helpers.jwt import generate_jwt
from ..helpers.verifyEmail import send_email


class UsersView(APIView):
    def get_queryset(self):
        queryset = Users.objects.select_related('department').all().values(
            'id', 'email', 'first_name', 'last_name', 'role', 'is_active', 
            'document_type', 'document_number', 'entity', 'cellphone', 
            'department__name', 'city', 'profession', 'reason', 'state', 
            'is_staff', 'last_login', 'is_superuser', 'date_joined'
        )
        return list(queryset)

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

    def get_object_for_delete(self, pk):
        try:
            return Users.objects.get(pk=pk)
        except Users.DoesNotExist:
            raise Http404

    def get(self, request, pk=None, format=None):
        users = self.get_object(pk)

        if isinstance(users, dict):
            users = [users]

        return Response(users)
    
    @transaction.atomic
    def post(self, request, format=None):
        adjusted_data = request.data.copy()
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        """ document_type = request.data.get('document_type')
        document_number = request.data.get('document_number') """
        """ cellphone = request.data.get('cellphone')
        department = request.data.get('department')
        city = request.data.get('city') """
        adjusted_data['rol'] = 4
        adjusted_data['is_active'] = 0
        adjusted_data['state'] = 'REVIEW'
        adjusted_data['is_staff'] = 0
        adjusted_data['last_login'] = None
        adjusted_data['is_superuser'] = 0
        adjusted_data['date_joined'] = timezone.now()

        if not all([email, password, first_name, last_name]):
            return Response({'msg': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        existing_user = Users.objects.filter(Q(email=email)).first()
        if existing_user:
            return Response({'msg': f'El usuario ya está registrado con el correo electrónico {existing_user.email}.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UsersCreateSerializer(data=adjusted_data)
        if serializer.is_valid():
            user = serializer.save()

            token = generate_jwt(user.email)  # Genera el token JWT
            user.token = token
            user.save()
            
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
            email_body = f'Hola {user.first_name},\n\nPor favor, verifica tu cuenta haciendo clic en el siguiente enlace:\n{verification_url}\n\nGracias.'
            send_email('Verificación de cuenta', email_body, user.email)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        user = get_object_or_404(Users, id=pk)
        adjusted_data = request.data

        # Actualizar solo los campos que están presentes en adjusted_data
        if 'email' in adjusted_data:
            email = adjusted_data['email']
            # Validar que el nuevo email no exista en otros usuarios
            if Users.objects.exclude(id=pk).filter(email=email).exists():
                return Response({'error': f'El correo electrónico {email} ya está registrado en otro usuario.'}, status=status.HTTP_400_BAD_REQUEST)
            user.email = email

        """ if 'document_number' in adjusted_data:
            document_number = adjusted_data['document_number']
            # Validar que el nuevo número de documento no exista en otros usuarios
            if Users.objects.exclude(id=pk).filter(document_number=document_number).exists():
                return Response({'error': f'El número de documento {document_number} ya está registrado en otro usuario.'}, status=status.HTTP_400_BAD_REQUEST)
            user.document_number = document_number """

        if 'first_name' in adjusted_data:
            user.first_name = adjusted_data['first_name']
        if 'last_name' in adjusted_data:
            user.last_name = adjusted_data['last_name']
        if 'rol' in adjusted_data:
            user.rol = adjusted_data['rol']
        """ if 'document_type' in adjusted_data:
            user.document_type = adjusted_data['document_type'] """
        if 'entity' in adjusted_data:
            user.entity = adjusted_data['entity']
        """ if 'cellphone' in adjusted_data:
            user.cellphone = adjusted_data['cellphone']
        if 'department' in adjusted_data:
            user.department = adjusted_data['department']
        if 'city' in adjusted_data:
            user.city = adjusted_data['city'] """
        if 'profession' in adjusted_data:
            user.profession = adjusted_data['profession']
        if 'is_active' in adjusted_data:
            user.is_active = adjusted_data['is_active']

        # Guardar los cambios
        user.save()

        # Serializar el usuario actualizado y devolver la respuesta
        serializer = UsersSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, format=None):
        user = self.get_object_for_delete(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class UsersStateView(APIView):
    def get_object_state(self, id):
        try:
            return Users.objects.get(id=id)
        except Users.DoesNotExist:
            raise Http404
        
    def put(self, request, pk, format=None):
        user = self.get_object_state(id=pk)
        newState = request.data.get('nuevoEstado')
        print('state', newState)        
        if newState in [0, 1]:
            user.is_active = newState
        # Aquí debes continuar actualizando los demás campos según tus necesidades
        user.save()  # Guardar los cambios
        serializer = UsersSerializer(user)  # Serializa el usuario actualizado
        return Response(serializer.data)
    
class SomeView(APIView):
    def get(self, request):
        # Acceder al usuario actual
        user = request.user
        if user.is_authenticated:
            # Realiza operaciones con el usuario
            return Response({"message": "Usuario autenticado"})
        else:
            return Response({"message": "Usuario no autenticado"})
        
class UserPermissionsView(APIView):
    def get(self, request):
        """ user = request.user """
        user = request.GET.get('email')
        print('user email: ', user)
        if user:
            try:
                user_role = Users.objects.filter(email=user).first()
                if user_role:
                    role_name = Rol.objects.filter(id=user_role.rol_id).first()
                    modules_with_permissions = UserModules.objects.filter(rol_id=user_role.rol_id)

                    modules_data = []
                    for module in modules_with_permissions:
                        page = Pages.objects.get(id=module.page_id)
                        permissions = {field.name: getattr(module, field.name) 
                                       for field in UserModules._meta.get_fields() 
                                       if field.name not in ['id', 'rol_id', 'page_id', 'page']}
                        module_data = {
                            'page_id': page.id,
                            'page_router': page.router,
                            'page_section' : page.section,
                            'page_name': page.title,
                            'page_icon': page.icon,
                            'page_subtitle': page.sub_title,
                            'permissions': permissions
                        }
                        modules_data.append(module_data)

                    return Response({
                        "role": role_name.name,  # Asumiendo que role_name es la relación a Roles
                        "modules": modules_data
                    })
                else:
                    return Response({"message": "Usuario no encontrado"}, status=404)

            except Rol.DoesNotExist:
                return Response({"message": "Rol no encontrado"}, status=404)

        else:
            return Response({"message": "Usuario no autenticado"}, status=401)
        
class RolesView(APIView):
    def get(self, request, format=None): 
        queryset = Rol.objects.all()
        serializer = RolSerializer(queryset, many=True)

        return Response(serializer.data)