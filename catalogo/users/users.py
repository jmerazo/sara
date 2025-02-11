from rest_framework.response import Response
from firebase_admin import auth
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.http import Http404
from rest_framework.views import APIView
from django.db.models import Q
from django.utils import timezone

from .serializers import UsersCreateSerializer, UsersSerializer, UsersValidateSerializer
from ..utils.serializers import RolSerializer
from .models import UserModules
from ..utils.models import Rol
from ..page.models import Pages
from ..models import Users, Departments, Cities
from ..helpers.jwt import generate_jwt_register
from ..helpers.Email import send_verification_email, send_acceptance_email, send_rejection_email

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

        # Verificar si el usuario ya existe
        existing_user = Users.objects.filter(Q(email=email)).first()
        if existing_user:
            return Response({
                'success': False,
                'message': f'El usuario ya está registrado con el correo electrónico {existing_user.email}.',
                'errors': {'email': ['El correo electrónico ya está registrado.']}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validar campos requeridos
        missing_fields = {}
        if not email:
            missing_fields['email'] = ['Este campo es obligatorio.']
        if not first_name:
            missing_fields['first_name'] = ['Este campo es obligatorio.']
        if not last_name:
            missing_fields['last_name'] = ['Este campo es obligatorio.']
        # Para registro normal, validar contraseña
        if not uuid_firebase and not password:
            missing_fields['password'] = ['La contraseña es obligatoria para registro normal.']

        if missing_fields:
            return Response({
                'success': False,
                'message': 'Faltan campos obligatorios.',
                'errors': missing_fields
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
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
                    'success': True,
                    'message': 'Usuario registrado exitosamente. Por favor, verifique su correo electrónico.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Error al registrar el usuario.',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Si hay algún error durante el proceso, eliminar el usuario local si fue creado
            if 'user' in locals():
                user.delete()
            if 'firebase_user' in locals():
                try:
                    auth.delete_user(firebase_user.uid)
                except:
                    pass  # Si falla la eliminación en Firebase, lo manejamos silenciosamente

            # Retornar una respuesta consistente con el formato de error
            return Response({
                'success': False,
                'message': 'Error durante el registro del usuario.',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        user = get_object_or_404(Users, id=pk)
        adjusted_data = request.data

        # Validaciones y actualizaciones de campos específicos
        if 'email' in adjusted_data:
            email = adjusted_data['email']
            # Validar que el nuevo email no exista en otros usuarios
            if Users.objects.exclude(id=pk).filter(email=email).exists():
                return Response(
                    {
                        'success': False,
                        'msg': f'El correo electrónico {email} ya está registrado en otro usuario.',
                        'data': None
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
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
                return Response(
                    {
                        'success': False,
                        'msg': 'El rol especificado no existe.',
                        'data': None
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        if 'document_type' in adjusted_data:
            user.document_type = adjusted_data['document_type']

        if 'cellphone' in adjusted_data:
            user.cellphone = adjusted_data['cellphone']

        if 'department' in adjusted_data:
            try:
                department_instance = Departments.objects.get(id=adjusted_data['department'])
                user.department = department_instance
            except Departments.DoesNotExist:
                return Response(
                    {
                        'success': False,
                        'msg': 'El departamento especificado no existe.',
                        'data': None
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        if 'city' in adjusted_data:
            try:
                city_instance = Cities.objects.get(id=adjusted_data['city'])
                user.city = city_instance
            except Cities.DoesNotExist:
                return Response(
                    {
                        'success': False,
                        'msg': 'La ciudad especificada no existe.',
                        'data': None
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        if 'is_active' in adjusted_data:
            user.is_active = adjusted_data['is_active']

        # Validación de datos usando el serializador con actualizaciones parciales
        serializer = UsersCreateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            # Guardar los cambios en la base de datos
            serializer.save()
            return Response(
                {
                    'success': True,
                    'msg': 'Usuario actualizado exitosamente.',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )

        # Si hay errores de validación, devolver los errores
        return Response(
            {
                'success': False,
                'msg': 'Error de validación en los datos proporcionados.',
                'data': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
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

                # Asignar el token al campo correspondiente del usuario (sin convertir a bytes)
                user.token = token  
                user.save()

                # Enviar correo de verificación para todos los usuarios
                send_verification_email(user, token)

                return Response({
                    'success': True,
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
        try:
            # Obtener el usuario por su ID
            user = self.get_object_state(id=pk)
            if not user:
                return Response(
                    {
                        'success': False,
                        'msg': 'El usuario no existe.',
                        'data': None
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            # Obtener el nuevo estado del cuerpo de la solicitud
            newState = request.data.get('nuevoEstado')

            # Validar que el nuevo estado sea válido (0 o 1)
            if newState not in [0, 1]:
                return Response(
                    {
                        'success': False,
                        'msg': 'El estado proporcionado no es válido. Debe ser 0 (inactivo) o 1 (activo).',
                        'data': None
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Actualizar el estado del usuario
            user.is_active = newState
            user.save()  # Guardar los cambios

            # Serializar el usuario actualizado
            serializer = UsersSerializer(user)

            # Retornar una respuesta exitosa
            return Response(
                {
                    'success': True,
                    'msg': 'Estado del usuario actualizado exitosamente.',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            # Manejar cualquier excepción inesperada
            return Response(
                {
                    'success': False,
                    'msg': f'Ocurrió un error inesperado: {str(e)}',
                    'data': None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class UsersValidateView(APIView):
    def get(self, request):
        try:
            queryset = Users.objects.filter(verificated=1, is_active=0)
            serializer = UsersValidateSerializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'Usuarios cargados satisfactoriamente',
                'data': {
                    'users': serializer.data,
                }
            }, status=status.HTTP_200_OK)
        except Users.DoesNotExist:
            return Response({
                'success': False,
                'message': 'No se encontraron usuarios.',
            }, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id, is_active=0)
            user.is_active = 1
            
            # Extraer el ID de rol desde el diccionario
            rol_id = request.data.get('rol')
            
            if rol_id is None:
                return Response({
                    'success': False,
                    'message': 'El rol es requerido para activar el usuario.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener la instancia del rol y asignarla al usuario
            rol_instance = get_object_or_404(Rol, id=rol_id)  # Asegura que el rol existe
            user.rol = rol_instance
            user.save()

            # Enviar el correo de aceptación
            send_acceptance_email(user)

            return Response({
                'success': True,
                'message': 'Usuario activado correctamente',
            }, status=status.HTTP_200_OK)
        
        except Users.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Usuario no encontrado o ya está activo.',
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error al activar el usuario: {str(e)}',
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)

            firebase_user_uid = user.uuid_firebase if hasattr(user, 'uuid_firebase') else None
            user.delete()

            # Eliminar usuario de Firebase
            if firebase_user_uid:
                try:
                    auth.delete_user(firebase_user_uid)
                except Exception as e:
                    pass  # Si hay un error eliminando en Firebase, lo manejamos silenciosamente

            # Enviar el correo de rechazo (opcional)
            send_rejection_email(user)

            return Response({
                'success': True,
                'message': 'Usuario eliminado correctamente',
            }, status=status.HTTP_200_OK)
        except Users.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Usuario no encontrado.',
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error al eliminar el usuario: {str(e)}',
            }, status=status.HTTP_400_BAD_REQUEST)      

class UserPermissionsView(APIView):
    def get(self, request):
        """ user = request.user """
        user = request.GET.get('email')

        # Array de permisos y módulos por defecto
        roles_permissions = {
            "ADMINISTRADOR": {
                "permissions": {
                    "add": 1,
                    "update": 1,
                    "delete": 1,
                    "download": 1,
                },
                "modules": {
                    "inicio": 1,
                    "especies": 1,
                    "familias": 1,
                    "evaluaciones": 1,
                    "monitoreos": 1,
                    "muestras": 1,
                    "datos_especies": 1,
                    "contadores": 1,
                    "mapa": 1,
                    "viveros": 1,
                    "admin": 1,
                },
            },
            "VERIFICADOR": {
                "permissions": {
                    "add": 0,
                    "update": 1,
                    "delete": 0,
                    "download": 1,
                },
                "modules": {
                    "inicio": 1,
                    "especies": 1,
                    "familias": 1,
                    "evaluaciones": 0,
                    "monitoreos": 0,
                    "muestras": 1,
                    "datos_especies": 0,
                    "contadores": 1,
                    "mapa": 0,
                    "viveros": 0,
                    "admin": 0,
                },
            },
            "TECNICO": {
                "permissions": {
                    "add": 1,
                    "update": 0,
                    "delete": 0,
                    "download": 0,
                },
                "modules": {
                    "inicio": 1,
                    "especies": 1,
                    "familias": 1,
                    "evaluaciones": 1,
                    "monitoreos": 1,
                    "muestras": 1,
                    "datos_especies": 1,
                    "contadores": 1,
                    "mapa": 0,
                    "viveros": 0,
                    "admin": 0,
                },
            },
            "USUARIO": {
                "permissions": {
                    "add": 0,
                    "update": 0,
                    "delete": 0,
                    "download": 0,
                },
                "modules": {
                    "inicio": 1,
                    "especies": 1,
                    "familias": 1,
                    "evaluaciones": 0,
                    "monitoreos": 0,
                    "muestras": 0,
                    "datos_especies": 0,
                    "contadores": 1,
                    "mapa": 0,
                    "viveros": 0,
                    "admin": 0,
                },
            },
            "USUARIO DEL BOSQUE": {
                "permissions": {
                    "add": 1,
                    "update": 0,
                    "delete": 0,
                    "download": 1,
                },
                "modules": {
                    "inicio": 1,
                    "especies": 1,
                    "familias": 1,
                    "evaluaciones": 0,
                    "monitoreos": 1,
                    "muestras": 0,
                    "datos_especies": 0,
                    "contadores": 1,
                    "mapa": 0,
                    "viveros": 1,
                    "admin": 0,
                },
            },
        }

        if user:
            try:
                # Obtener el usuario y su rol
                user_role = Users.objects.filter(email=user).first()
                if user_role:
                    role_name = Rol.objects.filter(id=user_role.rol_id).first()
                    role_name = role_name.name if role_name else "Rol desconocido"
                    modules_with_permissions = UserModules.objects.filter(rol_id=user_role.rol_id)

                    if not modules_with_permissions.exists():
                        # Si no hay módulos, usar permisos y módulos por defecto
                        default_role_data = roles_permissions.get(role_name, {})
                        return Response({
                            "role": role_name,
                            "permissions": default_role_data.get("permissions", {}),
                            "modules": default_role_data.get("modules", {}),
                        }, status=200)

                    # Procesar módulos con permisos asignados
                    modules_data = []
                    for module in modules_with_permissions:
                        page = Pages.objects.get(id=module.page_id)
                        permissions = {field.name: getattr(module, field.name) 
                                       for field in UserModules._meta.get_fields() 
                                       if field.name not in ['id', 'rol_id', 'page_id', 'page']}
                        module_data = {
                            'page_id': page.id,
                            'page_router': page.router,
                            'page_name': page.title,
                            'page_icon': page.icon,
                            'permissions': permissions
                        }
                        modules_data.append(module_data)

                    return Response({
                        "role": role_name,
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