from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import auth
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.http import Http404
from rest_framework.views import APIView
from django.db.models import Q
from django.utils import timezone

from .serializers import UsersCreateSerializer, UsersSerializer
from ..utils.serializers import RolSerializer
from .models import UserModules
from ..utils.models import Rol
from ..page.models import Pages
from ..models import Users, Departments, Cities
from ..helpers.jwt import generate_jwt, generate_jwt_register
from ..helpers.Email import send_verification_email


class UsersView(APIView):
    def get_queryset(self):
        queryset = Users.objects.select_related('department').all().values(
            'id', 'uuid_firebase', 'email', 'first_name', 'last_name', 'rol', 'is_active', 
            'document_type', 'document_number', 'cellphone', 
            'department', 'city', 'is_staff', 'last_login', 'is_superuser', 'date_joined'
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
            
    def post(self, request, format=None):
        user_fixed = request.data.copy()
        email = user_fixed.get('email')
        password = user_fixed.get('password')
        first_name = user_fixed.get('first_name')
        last_name = user_fixed.get('last_name')
        uuid_firebase = user_fixed.get('uuid_firebase')  # Para registro social

        # Ajustar datos como antes
        user_fixed['rol'] = 4
        user_fixed['is_active'] = 0
        user_fixed['is_staff'] = 0
        user_fixed['is_superuser'] = 0

        existing_user = Users.objects.filter(Q(email=email)).first()
        if existing_user:
            return Response({'msg': f'El usuario ya está registrado con el correo electrónico {existing_user.email}.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validar campos requeridos
            if not all([email, first_name, last_name]):
                return Response({'msg': 'Email, nombre y apellido son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

            # Para registro normal, validar contraseña
            if not uuid_firebase and not password:
                return Response({'msg': 'La contraseña es obligatoria para registro normal'}, status=status.HTTP_400_BAD_REQUEST)

            # Crear usuario en la base de datos local
            serializer = UsersCreateSerializer(data=user_fixed)
            if serializer.is_valid():
                user = serializer.save()
                
                # Si no es registro social, crear usuario en Firebase
                if not uuid_firebase:
                    firebase_user = auth.create_user(
                        email=email,
                        password=password,
                        display_name=f"{first_name} {last_name}"
                    )
                    user.uuid_firebase = firebase_user.uid
                else:
                    user.uuid_firebase = uuid_firebase

                # Generar token JWT y guardar
                token = generate_jwt_register(user.email)
                print('token ', token)
                user.token = token
                user.save()
                
                # Enviar correo de verificación para todos los usuarios
                send_verification_email(user, token)

                return Response({
                    'msg': 'Usuario registrado exitosamente. Por favor, verifique su correo electrónico.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Si hay algún error durante el proceso, eliminar el usuario local si fue creado
            if 'user' in locals():
                user.delete()
            if 'firebase_user' in locals():
                try:
                    auth.delete_user(firebase_user.uid)
                except:
                    pass  # Si falla la eliminación en Firebase, lo manejamos silenciosamente
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        user = get_object_or_404(Users, id=pk)
        adjusted_data = request.data

        # Validaciones y actualizaciones de campos específicos
        if 'email' in adjusted_data:
            email = adjusted_data['email']
            # Validar que el nuevo email no exista en otros usuarios
            if Users.objects.exclude(id=pk).filter(email=email).exists():
                return Response({'error': f'El correo electrónico {email} ya está registrado en otro usuario.'}, status=status.HTTP_400_BAD_REQUEST)
            user.email = email

        if 'first_name' in adjusted_data:
            user.first_name = adjusted_data['first_name']

        if 'last_name' in adjusted_data:
            user.last_name = adjusted_data['last_name']

        if 'rol' in adjusted_data:
            try:
                rol_instance = Rol.objects.get(id=adjusted_data['rol'])
                user.rol = rol_instance
            except Rol.DoesNotExist:
                return Response({'error': 'El rol especificado no existe.'}, status=status.HTTP_400_BAD_REQUEST)

        if 'document_type' in adjusted_data:
            user.document_type = adjusted_data['document_type']

        if 'cellphone' in adjusted_data:
            user.cellphone = adjusted_data['cellphone']

        if 'department' in adjusted_data:
            try:
                department_instance = Departments.objects.get(id=adjusted_data['department'])
                user.department = department_instance
            except Departments.DoesNotExist:
                return Response({'error': 'El departamento especificado no existe.'}, status=status.HTTP_400_BAD_REQUEST)

        if 'city' in adjusted_data:
            try:
                city_instance = Cities.objects.get(id=adjusted_data['city'])
                user.city = city_instance
            except Cities.DoesNotExist:
                return Response({'error': 'La ciudad especificada no existe.'}, status=status.HTTP_400_BAD_REQUEST)

        if 'is_active' in adjusted_data:
            user.is_active = adjusted_data['is_active']

        # Validación de datos usando el serializador con actualizaciones parciales
        serializer = UsersCreateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            # Guardar los cambios en la base de datos
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Si hay errores de validación, devolver los errores
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object_for_delete(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class UserRegisterView(APIView):
    def post(self, request, format=None):
        user_fixed = request.data.copy()
        email = user_fixed.get('email')
        password = user_fixed.get('password')
        first_name = user_fixed.get('first_name')
        last_name = user_fixed.get('last_name')
        uuid_firebase = user_fixed.get('uuid_firebase')  # Para registro social

        # Ajustar datos como antes
        user_fixed['rol'] = 4
        user_fixed['is_active'] = 0
        user_fixed['is_staff'] = 0
        user_fixed['is_superuser'] = 0

        existing_user = Users.objects.filter(Q(email=email)).first()
        if existing_user:
            return Response({'msg': f'El usuario ya está registrado con el correo electrónico {existing_user.email}.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validar campos requeridos
            if not all([email, first_name, last_name]):
                return Response({'msg': 'Email, nombre y apellido son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

            # Para registro normal, validar contraseña
            if not uuid_firebase and not password:
                return Response({'msg': 'La contraseña es obligatoria para registro normal'}, status=status.HTTP_400_BAD_REQUEST)

            # Crear usuario en la base de datos local
            serializer = UsersCreateSerializer(data=user_fixed)
            if serializer.is_valid():
                user = serializer.save()
                
                # Si no es registro social, crear usuario en Firebase
                if not uuid_firebase:
                    firebase_user = auth.create_user(
                        email=email,
                        password=password,
                        display_name=f"{first_name} {last_name}"
                    )
                    user.uuid_firebase = firebase_user.uid
                else:
                    user.uuid_firebase = uuid_firebase

                # Generar token JWT y guardar
                token = generate_jwt_register(user.email)
                user.token = token
                user.save()
                
                # Enviar correo de verificación para todos los usuarios
                send_verification_email(user, token)

                return Response({
                    'msg': 'Usuario registrado exitosamente. Por favor, verifique su correo electrónico.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Si hay algún error durante el proceso, eliminar el usuario local si fue creado
            if 'user' in locals():
                user.delete()
            if 'firebase_user' in locals():
                try:
                    auth.delete_user(firebase_user.uid)
                except:
                    pass  # Si falla la eliminación en Firebase, lo manejamos silenciosamente
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
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
                    }, status=200)
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