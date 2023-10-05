from rest_framework import viewsets, status, generics, permissions
from django.contrib.auth.backends import BaseBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.http import Http404
from django.contrib.auth import login, authenticate, logout
from rest_framework.views import APIView
from django.db.models import Q, Count
from decimal import Decimal
from .models import EspecieForestal, Glossary, CandidateTrees, Page, Users
from .serializers import EspecieForestalSerializer, NombresComunesSerializer, FamiliaSerializer, NombreCientificoSerializer, GlossarySerializer, GeoCandidateTreesSerializer, AverageTreesSerializer, PageSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            refresh = response.data.get('refresh')
            token = RefreshToken(refresh)
            user_id = token.payload.get('user_id')  # Obtén el ID del usuario desde el payload del token
            
            try:
                user_instance = Users.objects.get(id=user_id)  # Utiliza CustomUser en lugar de User
                # Accede a los campos adicionales de CustomUser
                email = user_instance.email
                document_type = user_instance.document_type
                document_number = user_instance.document_number
                cellphone = user_instance.cellphone
                entity = user_instance.entity
                profession = user_instance.profession
                rol = user_instance.rol
                first_name = user_instance.first_name
                last_name = user_instance.last_name
                state=user_instance.state
                is_staff=user_instance.is_staff
                is_superuser=user_instance.is_superuser
                # Agrega los campos al response.data
                user_data = {
                    'rol': rol,
                    'email': email,
                    'document_type': document_type,
                    'document_number': document_number,
                    'cellphone': cellphone,
                    'entity': entity,
                    'profession': profession,
                    'first_name': first_name,
                    'last_name': last_name,
                    'state': state,
                    'is_staff': is_staff,
                    'is_superuser': is_superuser
                }
                print('User data: ', user_data)
                # Devuelve una respuesta JSON con el diccionario de datos
                return Response({
                    'access': response.data['access'],
                    'refresh': response.data['refresh'],
                    'user_data': user_data,  # Agrega los datos del usuario
                })
                
            except Users.DoesNotExist:
                pass  # Si el usuario no existe, simplemente continua sin hacer nada
        
        return response

class LoginView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    # serializer_class = (permissions.AllowAny,)

    def post(self, request):
        asdsa = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            user_profile = user.userprofile  # Obtén el perfil asociado

            # Obtén el rol y tipo de usuario del perfil
            email = user_profile.email
            username = user_profile.username
            document_type = user_profile.document_type
            document_number = user_profile.document_number
            cellphone = user_profile.cellphone
            entity = user_profile.entity
            profession = user_profile.profession
            rol = user_profile.rol
            first_name = user_profile.first_name
            last_name = user_profile.last_name

            return Response({
                'user': user.to_dict(),
                'profile': {
                    'email': email,
                    'document_type': document_type,
                    'document_number': document_number,
                    'cellphone': cellphone,
                    'entity': entity,
                    'profession': profession,
                    'rol': rol,
                    'first_name': first_name,
                    'last_name': last_name
                }
            }, status=200)
        else:
            return Response({'error': 'Invalid email or password'}, status=401)
        
class LogoutView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        logout(request)
        return Response({'success': 'Successfully logged out'}, status=200)

class CurrentUser(viewsets.ModelViewSet):
     def get_queryset(self):
      user = self.request.user 
      return self.serializer_class.Meta.model.objects.filter(usuario=user)

class EspecieForestalView(viewsets.ModelViewSet):
    queryset = EspecieForestal.objects.all()
    serializer_class = EspecieForestalSerializer

    @action(detail=True, methods=['GET'])
    def get_image_links(self, request, pk=None):
        especie = self.get_object()
        image_links = {
            'foto_general': self._get_image_link(especie.foto_general),
            'foto_hojas': self._get_image_link(especie.foto_hojas),
            'foto_flor': self._get_image_link(especie.foto_flor),
            'foto_fruto': self._get_image_link(especie.foto_fruto),
            'foto_semillas': self._get_image_link(especie.foto_semillas),
        }
        return Response(image_links)

    def _get_image_link(self, image_relative_path):
        # Reutiliza la lógica para construir el enlace de descarga directa de Google Drive
        base_drive_url = "https://drive.google.com/uc?export=download&id="
        full_drive_url = base_drive_url + extract_file_id(image_relative_path)
        return full_drive_url

class NombresComunesView(viewsets.ModelViewSet):
   queryset = EspecieForestal.objects.all()
   serializer_class = NombresComunesSerializer

class FamiliaView(viewsets.ViewSet):
    serializer_class = FamiliaSerializer

    #Aquí se realizó la función para enviar las familias sin duplicados
    def list(self, request, *args, **kwargs):
        queryset = EspecieForestal.objects.values('familia').distinct()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class NombreCientificoView(viewsets.ModelViewSet):
   queryset = EspecieForestal.objects.all()
   serializer_class = NombreCientificoSerializer

class SuggestionTypeView(APIView):
    def get(self, request, types, format=None):
        if types == 'familia':
            queryset = EspecieForestal.objects.values_list('familia', flat=True)
        elif types == 'nom_comunes':
            queryset = EspecieForestal.objects.values_list('nom_comunes', flat=True)
        elif types == 'nombre_cientifico':
            queryset = EspecieForestal.objects.values_list('nombre_cientifico', flat=True)
        else:
            queryset = []

        return Response(list(queryset))

suggestion_type_view = SuggestionTypeView.as_view()

class BuscarEspecieView(APIView):
    def get(self, request, nombre, format=None):        
        search = EspecieForestal.objects.filter(nom_comunes__icontains=nombre).first()
        serializer = EspecieForestalSerializer(search)
        
        return Response(serializer.data)
    
class BuscarFamiliaView(APIView):
    def get(self, request, familia, format=None):        
        search = EspecieForestal.objects.filter(familia__icontains=familia)
        serializer = EspecieForestalSerializer(search, many=True)
        
        return Response(serializer.data)

class FamiliasView(APIView):
    def get(self, request, format=None):
        # Obtener las familias
        familias = EspecieForestal.objects.values('familia').annotate(total=Count('familia')).distinct()

        resultado = []

        # Recorrer las familias
        for familia in familias:
            familia_nombre = familia['familia']

            # Obtener las especies relacionadas a la familia actual
            especies = EspecieForestal.objects.filter(familia=familia_nombre)

            # Crear una lista de nombres de especies
            especies_nombres = [especie.nom_comunes for especie in especies]

            # Agregar la familia y las especies a la lista de resultados
            resultado.append({
                'familia': familia_nombre,
                'especies': especies_nombres
            })

        return Response(resultado)
    
class ScientificNameView(APIView):
    def get(self, request, scientific, format=None):        
        search = EspecieForestal.objects.filter(nombre_cientifico__icontains=scientific).first()
        serializer = EspecieForestalSerializer(search)
        
        return Response(serializer.data)

class GlossaryView(APIView):
    def get(self, request, format=None): 
        queryset = Glossary.objects.all()
        serializer = GlossarySerializer(queryset, many=True)

        return Response(serializer.data)
    
class GeoCandidateTreesView(APIView):
    def get(self, request, format=None): 
        geo = CandidateTrees.objects.all()
        geoData = GeoCandidateTreesSerializer(geo, many=True).data

        geo_format = []

        for datos in geoData:
            latitud, longitud  = datos['abcisa_xy'].split(', ')
            code_number = int(datos['cod_especie'])
            geo_fixed = {'codigo': code_number, 'lat': float(latitud), 'lon': float(longitud)}
            geo_format.append(geo_fixed)

        """ print('Coordendas', geo_format) """
        return Response(geo_format)

class AverageCandidateTreesView(APIView):
    def convert_to_decimal_or_int(self, value):
        try:
            return Decimal(value)
        except (TypeError, ValueError):
            try:
                return int(value)
            except (TypeError, ValueError):
                return None

    def get(self, request, format=None): 
        try:
            average = CandidateTrees.objects.all()
            averageData = AverageTreesSerializer(average, many=True).data

            average_format = []

            for datos in averageData:
                code_number = int(datos['cod_especie'])

                altura_total_str = datos['altura_total']
                at = self.convert_to_decimal_or_int(altura_total_str)

                altura_ccial_str = datos['altura_comercial']
                ac = self.convert_to_decimal_or_int(altura_ccial_str)

                average_fixed = {'codigo': code_number, 'altitud': datos['altitud'], 'altura_total': at, 'altura_comercial': ac, 'cobertura': datos['cobertura']}
                average_format.append(average_fixed)

            """ print('Average data: ', average_format) """
            return Response(average_format)

        except Exception as e:
            print('Error:', str(e))
            return Response({'error': 'Ocurrió un error al obtener los datos'}, status=500)
            
class PageView(APIView):
    def get_object(self, pk=None):
        if pk is not None:
            try:
                return Page.objects.get(pk=pk)
            except Page.DoesNotExist:
                raise Http404
        else:
            return Page.objects.all()

    def get(self, request, pk=None, format=None):
        pages = self.get_object(pk)
        
        if isinstance(pages, Page):
            serializer = PageSerializer(pages)
        else:
            serializer = PageSerializer(pages, many=True)
            
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        page = self.get_object(pk)
        serializer = PageSerializer(page, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        page = self.get_object(pk)
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)