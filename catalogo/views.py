from rest_framework import viewsets, status, generics, permissions
from PIL import Image
from io import BytesIO
from django.db import connection, transaction
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth import login, authenticate, logout
from rest_framework.views import APIView
from django.db.models import Q, Count, Value, CharField, Count, Sum, Case, When, IntegerField
from django.db.models.functions import Coalesce
from django.db import connection
from decimal import Decimal
import random, string, shutil, os, tempfile, base64
from django.conf import settings
from .models import EspecieForestal, Glossary, CandidateTrees, Page, Users, Monitoring, Samples, ImagesSpeciesRelated
from .serializers import EspecieForestalSerializer, CandidateTreesSerializer,NombresComunesSerializer, FamiliaSerializer, ImagesSpeciesRelatedSerializer, NombreCientificoSerializer, GlossarySerializer, GeoCandidateTreesSerializer, AverageTreesSerializer, PageSerializer, MonitoringsSerializer, SamplesSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

def save_image(image, cod_especie, nom_comunes, image_type):
    # Carpeta principal para las imágenes
    base_dir = 'images'

    # Carpeta secundaria con el código de especie y nombre común
    sub_dir = os.path.join(base_dir, f"{cod_especie}_{nom_comunes}")

    # Carpeta tercera con el nombre de la imagen
    os.makedirs(sub_dir, exist_ok=True)

    # Nombre del archivo de imagen basado en el tipo (imgLeaf, imgFlower, etc.)
    file_name = f"{image_type}_{cod_especie}_{nom_comunes}.jpg"

    # Ruta completa del archivo
    file_path = os.path.join(sub_dir, file_name)

    with open(file_path, 'wb') as f:
        for chunk in image.chunks():
            f.write(chunk)

    return file_path

def generate_random_id(length):
            characters = string.ascii_letters + string.digits
            random_id = ''.join(random.choice(characters) for _ in range(length))
            return random_id


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
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)

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

class EspecieForestalView(APIView):
    def get_object(self, pk=None):
        if pk is not None:
            try:
                return EspecieForestal.objects.get(ShortcutID=pk)
            except EspecieForestal.DoesNotExist:
                raise Http404
        else:
            return EspecieForestal.objects.all()

    def get(self, request, pk=None, format=None):
        if pk is not None:
            # Si se proporciona un pk, devuelve un objeto específico
            specie = self.get_object(pk)
            serializer = EspecieForestalSerializer(specie)
        else:
            # Si no se proporciona un pk, devuelve la lista completa
            species = self.get_object()
            serializer = EspecieForestalSerializer(species, many=True)

        return Response(serializer.data)
    
    @transaction.atomic
    def post(self, request, format=None):
        adjusted_data = request.data.copy()

        ce = adjusted_data.get('cod_especie')

        existing_specie = EspecieForestal.objects.filter(cod_especie=ce).first()
        if existing_specie:
            return Response({'error': f'El código de espeie {ce} ya está registrado en otra especie.'}, status=status.HTTP_400_BAD_REQUEST)

        while True:
            random_id = generate_random_id(8)
            existing_code = EspecieForestal.objects.filter(ShortcutID=random_id).first()
            
            if existing_code is None:
                # El ID no existe en la base de datos, se puede utilizar
                break
        
        cod_especie_img= adjusted_data['cod_especie']
        nom_comunes_img = adjusted_data['nom_comunes']
        imgGeneral = adjusted_data['imageInputGeneral']
        imgLeaf = adjusted_data['imageInputLeaf']
        imgFlower = adjusted_data['imageInputFlower']
        imgFruit = adjusted_data['imageInputFruit']
        imgSeed = adjusted_data['imageInputSeed']
        imgStem = adjusted_data['imageInputStem']
        imgLandScapeOne = adjusted_data['imageInputLandScapeOne']
        imgLandScapeTwo = adjusted_data['imageInputLandScapeTwo']
        imgLandScapeThree = adjusted_data['imageInputLandScapeThree']

        # Crear la carpeta principal con el código de especie y nombre común
        base_dir = 'images'
        sub_dir = os.path.join(base_dir, f"{cod_especie_img}_{nom_comunes_img}")

        os.makedirs(sub_dir, exist_ok=True)  # Asegúrate de que la carpeta principal exista

        # Crear carpetas para cada tipo de imagen
        img_types = {
            'imgGeneral': imgGeneral,
            'imgLeaf': imgLeaf,
            'imgFlower': imgFlower,
            'imgFruit': imgFruit,
            'imgSeed': imgSeed,
            'imgStem': imgStem,
            'imgLandScapeOne': imgLandScapeOne,
            'imgLandScapeTwo': imgLandScapeTwo,
            'imgLandScapeThree': imgLandScapeThree,
        }

        # Mapea cada nombre de imagen a un nombre más manejable
        img_names = {
            'imgGeneral': 'imgGeneral',
            'imgLeaf': 'imgLeaf',
            'imgFlower': 'imgFlower',
            'imgFruit': 'imgFruit',
            'imgSeed': 'imgSeed',
            'imgStem': 'imgStem',
            'imgLandScapeOne': 'imgLandScapeOne',
            'imgLandScapeTwo': 'imgLandScapeTwo',
            'imgLandScapeThree': 'imgLandScapeThree',
        }

        # Longitud de la cadena alfanumérica
        length = 5

        # Función para generar un nombre alfanumérico aleatorio
        def generate_random_filename(length):
            characters = string.ascii_letters + string.digits
            return ''.join(random.choice(characters) for _ in range(length))

        # Recorre las imágenes y realiza la copia con nombres aleatorios
        for img_type, img_data in img_types.items():
            if img_data:
                # Genera un nombre alfanumérico aleatorio para el archivo
                random_filename = generate_random_filename(5)
                
                # Obtiene la extensión del archivo
                file_extension = ".jpeg"  # Reemplaza con la extensión de archivo adecuada

                # Construye la ruta de destino en la subcarpeta correspondiente
                destination_path = os.path.join(sub_dir, img_type, f"{img_type}_{random_filename}{file_extension}")

                # Asegúrate de que la carpeta exista o créala si no existe
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)

                # Decodifica los datos base64 y guarda la imagen en formato JPEG
                img_data = img_data.split(';base64,')[-1]
                img_data_bytes = base64.b64decode(img_data)

                with open(destination_path, 'wb') as dest_file:
                    dest_file.write(img_data_bytes)

                img_related = ImagesSpeciesRelated()

                image_columns = {
                    'img_general': 'imgGeneral',
                    'img_leafs': 'imgLeaf',
                    'img_fruits': 'imgFruit',
                    'img_flowers': 'imgFlower',
                    'img_seeds': 'imgSeed',
                    'img_stem': 'imgStem',
                    'img_landscape_one': 'imgLandScapeOne',
                    'img_landscape_two': 'imgLandScapeTwo',
                    'img_landscape_three': 'imgLandScapeThree',
                }

                # Agrega el specie_id a la instancia de ImagesSpeciesRelated
                img_related.specie_id = random_id

                # Itera a través del diccionario y verifica si la imagen está cargada antes de asignarla al campo correspondiente
                for column_name, img_type in image_columns.items():
                    if img_types[img_type]:  # Verifica si la imagen está cargada
                        setattr(img_related, column_name, destination_path)

                # Guarda la instancia en la base de datos solo si al menos un campo tiene una imagen cargada
                if any(getattr(img_related, column) for column in image_columns):
                    img_related.save()

                print(f"Archivo copiado a: {destination_path}")

        """ # Crea una instancia de ImagesSpeciesRelated con los datos
        img_related = ImagesSpeciesRelated(
            specie_id=random_id,
            img_general=f"{sub_dir}/{img_types['imgGeneral']}/{img_types['imgGeneral']}_{cod_especie_img}_{nom_comunes_img}",
            img_leafs=f"{sub_dir}/{img_types['imgLeaf']}/{img_types['imgLeaf']}_{cod_especie_img}_{nom_comunes_img}",
            img_fruits=f"{sub_dir}/{img_types['imgFruit']}/{img_types['imgFruit']}_{cod_especie_img}_{nom_comunes_img}",
            img_flowers=f"{sub_dir}/{img_types['imgFlower']}/{img_types['imgFlower']}_{cod_especie_img}_{nom_comunes_img}",
            img_seeds=f"{sub_dir}/{img_types['imgSeed']}/{img_types['imgSeed']}_{cod_especie_img}_{nom_comunes_img}",
            img_stem=f"{sub_dir}/{img_types['imgStem']}/{img_types['imgStem']}_{cod_especie_img}_{nom_comunes_img}",
            img_landscape_one=f"{sub_dir}/{img_types['imgLandScapeOne']}/{img_types['imgLandScapeOne']}_{cod_especie_img}_{nom_comunes_img}",
            img_landscape_two=f"{sub_dir}/{img_types['imgLandScapeTwo']}/{img_types['imgLandScapeTwo']}_{cod_especie_img}_{nom_comunes_img}",
            img_landscape_three=f"{sub_dir}/{img_types['imgLandScapeThree']}/{img_types['imgLandScapeThree']}_{cod_especie_img}_{nom_comunes_img}",
        )

        # Guarda la instancia en la base de datos
        img_related.save() """


        serializer = EspecieForestalSerializer(data=adjusted_data)
        if serializer.is_valid():
            specie = EspecieForestal(
                ShortcutID = random_id,
                cod_especie = adjusted_data['cod_especie'],
                nom_comunes = adjusted_data['nom_comunes'],
                otros_nombres = adjusted_data['otros_nombres'],
                nombre_cientifico = adjusted_data['nombre_cientifico'],
                sinonimos = adjusted_data['sinonimos'],
                familia = adjusted_data['familia'],
                distribucion = adjusted_data['distribucion'],
                habito = adjusted_data['habito'],
                follaje = adjusted_data['follaje'],
                forma_copa = adjusted_data['forma_copa'],
                tipo_hoja = adjusted_data['tipo_hoja'],
                disposicion_hojas = adjusted_data['disposicion_hojas'],
                hojas = adjusted_data['hojas'],
                flor = adjusted_data['flor'],
                frutos = adjusted_data['frutos'],
                semillas = adjusted_data['semillas'],
                tallo = adjusted_data['tallo'],
                raiz = adjusted_data['raiz']
            )
            specie.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def put(self, request, pk, format=None):
        specie = get_object_or_404(EspecieForestal, ShortcutID=pk)
        adjusted_data = request.data

        cod_specie_currently = specie.cod_especie

        # Aquí puedes realizar las validaciones y actualizaciones necesarias.
        # Por ejemplo, para actualizar el email y el número de documento:
        cod_especie_new = adjusted_data.get('cod_especie')
        nom_comunes = adjusted_data.get('nom_comunes')
        otros_nombres = adjusted_data.get('otros_nombres')
        nombre_cientifico = adjusted_data.get('nombre_cientifico')
        sinonimos = adjusted_data.get('sinonimos')
        familia = adjusted_data.get('familia')
        distribucion = adjusted_data.get('distribucion')
        habito = adjusted_data.get('habito')
        follaje = adjusted_data.get('follaje')
        forma_copa = adjusted_data.get('forma_copa')
        tipo_hoja = adjusted_data.get('tipo_hoja')
        disposicion_hojas = adjusted_data.get('disposicion_hojas')
        hojas = adjusted_data.get('hojas')
        flor = adjusted_data.get('flor')
        frutos = adjusted_data.get('frutos')
        semillas = adjusted_data.get('semillas')
        tallo = adjusted_data.get('tallo')
        raiz = adjusted_data.get('raiz')
        
        # Asegurémonos de que el nuevo email o número de documento no existan en otros usuarios
        if cod_specie_currently != cod_especie_new:
            existing_specie = EspecieForestal.objects.exclude(ShortcutID=pk).filter(cod_especie=cod_especie_new).first()
            if existing_specie:
                return Response({'error': f'El código de espeie {cod_especie_new} ya está registrado en otra especie.'}, status=status.HTTP_400_BAD_REQUEST)

        # Actualizamos los campos del usuario
        specie.cod_especie = cod_especie_new
        specie.nom_comunes = nom_comunes
        specie.otros_nombres = otros_nombres
        specie.nombre_cientifico = nombre_cientifico
        specie.sinonimos = sinonimos
        specie.familia = familia
        specie.distribucion = distribucion
        specie.habito = habito
        specie.follaje = follaje
        specie.forma_copa = forma_copa
        specie.tipo_hoja = tipo_hoja
        specie.disposicion_hojas = disposicion_hojas
        specie.hojas = hojas
        specie.flor = flor
        specie.frutos = frutos
        specie.semillas = semillas
        specie.tallo = tallo
        specie.raiz = raiz        

        # Aquí debes continuar actualizando los demás campos según tus necesidades

        specie.save()  # Guardar los cambios

        serializer = EspecieForestalSerializer(specie)  # Serializa el usuario actualizado
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        specie = self.get_object(pk)
        specie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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

class FamiliaView(APIView):
    serializer_class = FamiliaSerializer

    def get(self, request, format=None):
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
        # Realizar la consulta SQL
        sql_query = """
            SELECT ea.cod_especie, ea.numero_placa, ef.nom_comunes, ef.nombre_cientifico, ea.vereda, ea.nombre_del_predio, ea.abcisa_xy, ea.resultado 
            FROM evaluacion_as AS ea 
            INNER JOIN especie_forestal AS ef ON ea.cod_especie = ef.cod_especie
        """
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            results = cursor.fetchall()

        # Procesar los resultados
        geo_format = []
        for datos in results:
            cod_especie, numero_placa, nom_comunes, nombre_cientifico, vereda, nombre_del_predio, abcisa_xy, resultado = datos
            latitud, longitud  = abcisa_xy.split(', ')
            
            geo_fixed = {
                'codigo': int(cod_especie),
                'numero_placa': numero_placa,
                'vereda': vereda,
                'nombre_del_predio': nombre_del_predio,
                'lat': float(latitud),
                'lon': float(longitud),
                'coordenadas': abcisa_xy,
                'resultado': resultado,
                'nom_comunes': nom_comunes,
                'nombre_cientifico': nombre_cientifico,
            }
            geo_format.append(geo_fixed)

        return Response(geo_format)
    
class CandidatesTreesView(APIView):
    def get(self, request, format=None): 
        queryset = CandidateTrees.objects.all()
        serializer = CandidateTreesSerializer(queryset, many=True)

        return Response(serializer.data)

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
    

# VISTAS MONITOREOS
class SearchMonitoringCandidateView(APIView):
    def get(self, request, id, format=None):        
        search = Monitoring.objects.filter(ShortcutIDEV=id)
        serializer = MonitoringsSerializer(search, many=True)
        
        return Response(serializer.data)

class SearchMonitoringSpecieView(APIView):
    def get(self, request, code, format=None):
        # Obtener los valores de ShortcutIDEV desde la subconsulta
        shortcut_idevs = CandidateTrees.objects.filter(cod_especie=code).values('ShortcutIDEV')
        
        # Realizar la búsqueda en la tabla Monitoring usando esos valores
        search = Monitoring.objects.filter(ShortcutIDEV__in=shortcut_idevs)
        
        serializer = MonitoringsSerializer(search, many=True)
        
        return Response(serializer.data)
    
class ReportSpecieDataView(APIView):
    def get(self, request, format=None):
        query = """
        SELECT
            ef.cod_especie,
            ef.nom_comunes,
            ef.nombre_cientifico,
            COUNT(DISTINCT e.ShortcutIDEV) AS evaluados,
            SUM(CASE WHEN m.ShortcutIDEV IS NOT NULL THEN 1 ELSE 0 END) AS monitoreos,
            SUM(CASE WHEN mu.nro_placa IS NOT NULL THEN 1 ELSE 0 END) AS muestras
        FROM especie_forestal AS ef
        LEFT JOIN evaluacion_as AS e ON ef.cod_especie = e.cod_especie
        LEFT JOIN monitoreo AS m ON e.ShortcutIDEV = m.ShortcutIDEV
        LEFT JOIN muestras AS mu ON e.ShortcutIDEV = mu.nro_placa
        WHERE e.numero_placa IS NOT NULL AND e.numero_placa != ''
        GROUP BY ef.cod_especie, ef.nom_comunes, ef.nombre_cientifico;
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            
        data = []
        for row in results:
            item = {
                'cod_especie': row[0],
                'nom_comunes': row[1],
                'nombre_cientifico': row[2],
                'evaluados': row[3],
                'monitoreos': row[4],
                'muestras': row[5],
            }
            data.append(item)
        
        return Response(data)
    
class SearchCandidatesSpecieView(APIView):
    def get(self, request, nom, format=None):
        # Define la consulta SQL con un marcador de posición para nom
        sql = """
            SELECT ea.ShortcutIDEV, ea.numero_placa, ea.cod_expediente, ea.cod_especie, ea.fecha_evaluacion, ea.departamento, ea.municipio, ea.altitud, ea.altura_total, ea.altura_comercial, ea.cobertura, ea.cober_otro, ea.entorno_individuo, ea.entorno_otro, ea.especies_forestales_asociadas, ea.dominancia_if, ea.forma_fuste, ea.dominancia, ea.alt_bifurcacion, ea.estado_copa, ea.posicion_copa, ea.fitosanitario, ea.presencia, ea.resultado, ea.evaluacion, ea.observaciones
            FROM evaluacion_as AS ea
            INNER JOIN especie_forestal AS ef ON ea.cod_especie = ef.cod_especie
            WHERE ef.nom_comunes = '%s';
        """
        """         print("SQL:", sql % nom) """
        # Ejecuta la consulta con el valor de nom
        with connection.cursor() as cursor:
            cursor.execute(sql % nom)
            result = cursor.fetchall()

            columns = [column[0] for column in cursor.description if column[0] is not None]

            # Filtra las filas que contienen valores NULL y sustituye 'None' por None
            queryset = []
            for row in result:
                row_dict = {}
                for idx, col in enumerate(columns):
                    value = row[idx]
                    if value == 'None':
                        value = None
                    row_dict[col] = value
                queryset.append(row_dict)

            return Response(queryset)

