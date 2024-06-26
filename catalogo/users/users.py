from ..models import Users
from .serializers import UsersSerializer
from rest_framework.response import Response
from django.db import connection, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.http import Http404
from rest_framework.views import APIView
from django.db.models import Q
import random, string
from django.utils import timezone
from django.contrib.auth.models import Group, Permission
from rest_framework.permissions import IsAuthenticated
from .models import Roles, UserModules
from ..page.models import Pages
from .users import Users

def generate_random_id(length):
            characters = string.ascii_letters + string.digits
            random_id = ''.join(random.choice(characters) for _ in range(length))
            return random_id

class UsersView(APIView):
    def get_queryset(self):
        # Consulta SQL directa
        query = """
            SELECT 
                u.id, 
                u.email, 
                u.first_name, 
                u.last_name, 
                u.rol, 
                u.is_active, 
                u.document_type, 
                u.document_number, 
                u.entity, 
                u.cellphone, 
                u.department, 
                d.name, 
                u.city, 
                u.profession, 
                u.reason, 
                u.state, 
                u.is_staff, 
                u.last_login, 
                u.is_superuser, 
                u.date_joined
            FROM Users AS u
            INNER JOIN departments AS d ON u.department = d.code
        """
        # Ejecutar la consulta
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        columns = [
            'id', 
            'email', 
            'first_name', 
            'last_name', 
            'rol', 
            'is_active', 
            'document_type', 
            'document_number', 
            'entity', 
            'cellphone', 
            'department', 
            'name', 
            'city', 
            'profession', 
            'reason', 
            'state', 
            'is_staff', 
            'last_login', 
            'is_superuser', 
            'date_joined'
        ]
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
        
    def get_object_for_delete(self, pk):
        # Este método se utiliza específicamente para la acción de eliminación.
        try:
            return Users.objects.get(pk=pk)
        except Users.DoesNotExist:
            raise Http404

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
            user.save()  # Guarda el usuario antes de asignarle el grupo

            default_group = Group.objects.get(name='DEFAULT')
            user.groups.add(default_group)

            default_permission = Permission.objects.get(codename='view_user')
            user.user_permissions.add(default_permission)

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

        if 'document_number' in adjusted_data:
            document_number = adjusted_data['document_number']
            # Validar que el nuevo número de documento no exista en otros usuarios
            if Users.objects.exclude(id=pk).filter(document_number=document_number).exists():
                return Response({'error': f'El número de documento {document_number} ya está registrado en otro usuario.'}, status=status.HTTP_400_BAD_REQUEST)
            user.document_number = document_number

        if 'first_name' in adjusted_data:
            user.first_name = adjusted_data['first_name']
        if 'last_name' in adjusted_data:
            user.last_name = adjusted_data['last_name']
        if 'rol' in adjusted_data:
            user.rol = adjusted_data['rol']
        if 'document_type' in adjusted_data:
            user.document_type = adjusted_data['document_type']
        if 'entity' in adjusted_data:
            user.entity = adjusted_data['entity']
        if 'cellphone' in adjusted_data:
            user.cellphone = adjusted_data['cellphone']
        if 'department' in adjusted_data:
            user.department = adjusted_data['department']
        if 'city' in adjusted_data:
            user.city = adjusted_data['city']
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
                    role_name = Roles.objects.filter(id=user_role.rol_id).first()
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

            except Roles.DoesNotExist:
                return Response({"message": "Rol no encontrado"}, status=404)

        else:
            return Response({"message": "Usuario no autenticado"}, status=401)