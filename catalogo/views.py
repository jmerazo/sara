from rest_framework import viewsets, status, generics, permissions
from PIL import Image
from io import BytesIO
from collections import namedtuple
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
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.http import JsonResponse

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

# VISTAS ESPECIES FORESTALES
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
        # Realizar la consulta SQL personalizada
        query = """
            SELECT * 
            FROM especie_forestal AS ef 
            LEFT JOIN img_species AS i ON ef.ShortcutID = i.specie_id;
        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            try:
                rows = cursor.fetchall()
                if rows:
                    columns = [col[0] for col in cursor.description]

                    # Procesar los datos obtenidos de la consulta SQL personalizada
                    species_data = []
                    for row in rows:
                        data = {}
                        for col, value in zip(columns, row):
                            data[col] = value
                        species_data.append(data)

                    return Response(species_data)  # Devuelve directamente los datos obtenidos
                else:
                    return Response([])  # Devuelve una lista vacía si no hay resultados
            except Exception as e:
                return Response({"error": str(e)})  # Devuelve un mensaje de error en caso de excepción
    
    
    @transaction.atomic
    def post(self, request, format=None):
        adjusted_data = request.data.copy()

        ce = adjusted_data.get('cod_especie')

        existing_specie = EspecieForestal.objects.filter(cod_especie=ce).first()
        if existing_specie:
            return Response({'error': f'El código de especie {ce} ya está registrado en otra especie.'}, status=status.HTTP_400_BAD_REQUEST)

        while True:
            random_id = generate_random_id(8)
            existing_code = EspecieForestal.objects.filter(ShortcutID=random_id).first()
            
            if existing_code is None:
                # El ID no existe en la base de datos, se puede utilizar
                break

        cod_especie_img = adjusted_data['cod_especie']
        nom_comunes_img = adjusted_data['nom_comunes']

        base_dir = 'images'
        sub_dir = os.path.join(base_dir, f"{cod_especie_img}_{nom_comunes_img}")
        os.makedirs(sub_dir, exist_ok=True)  # Asegúrate de que la carpeta principal exista

        imgGeneral = adjusted_data['imageInputGeneral']
        imgLeaf = adjusted_data['imageInputLeaf']
        imgFlower = adjusted_data['imageInputFlower']
        imgFruit = adjusted_data['imageInputFruit']
        imgSeed = adjusted_data['imageInputSeed']
        imgStem = adjusted_data['imageInputStem']
        imgLandScapeOne = adjusted_data['imageInputLandScapeOne']
        imgLandScapeTwo = adjusted_data['imageInputLandScapeTwo']
        imgLandScapeThree = adjusted_data['imageInputLandScapeThree']

        img_related = ImagesSpeciesRelated()
        img_related.specie_id = random_id

        image_columns = {
            'img_general': imgGeneral,
            'img_leafs': imgLeaf,
            'img_fruits': imgFruit,
            'img_flowers': imgFlower,
            'img_seeds': imgSeed,
            'img_stem': imgStem,
            'img_landscape_one': imgLandScapeOne,
            'img_landscape_two': imgLandScapeTwo,
            'img_landscape_three': imgLandScapeThree,
        }

        # Arreglo adicional para validar nombres de archivo
        valid_image_names = {
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

        # Función para generar un nombre alfanumérico aleatorio
        def generate_random_filename(length):
            characters = string.ascii_letters + string.digits
            return ''.join(random.choice(characters) for _ in range(length))

        img_related = ImagesSpeciesRelated()
        img_related.specie_id = random_id

        for column_name, img_data in image_columns.items():
            if img_data:
                random_filename = generate_random_filename(8)
                file_extension = ".jpeg"  # Reemplaza con la extensión de archivo adecuada

                valid_image_name = valid_image_names[column_name]
                destination_path = os.path.join(sub_dir, f"{valid_image_name}_{random_filename}{file_extension}")

                img_data = img_data.split(';base64,')[-1]
                img_data_bytes = base64.b64decode(img_data)

                with open(destination_path, 'wb') as dest_file:
                    dest_file.write(img_data_bytes)

                setattr(img_related, column_name, destination_path)
                print(f"Imagen asignada a {column_name}")

        img_related.save()

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

class BuscarEspeciezView(APIView):
    def get(self, request, nombre, format=None):        
        search = EspecieForestal.objects.filter(nom_comunes__icontains=nombre).first()
        serializer = EspecieForestalSerializer(search)

        return Response(serializer.data)

class BuscarEspecieView(APIView):
    def get(self, request, code, format=None):
        sql_query = """
        SELECT 
            ef.ShortcutID,
            ef.cod_especie,
            ef.nom_comunes,
            ef.otros_nombres,
            ef.nombre_cientifico,
            ef.nombre_cientifico_especie,
            ef.nombre_autor_especie,
            ef.sinonimos,
            ef.familia,
            i.img_general,
            ef.distribucion,
            ef.habito,
            ef.follaje,
            ef.forma_copa,
            ef.tipo_hoja,
            ef.disposicion_hojas,
            ef.hojas,
            i.img_leafs,
            ef.flor,
            i.img_flowers,
            ef.frutos,
            i.img_fruits,
            ef.semillas,
            i.img_seeds,
            ef.tallo,
            i.img_stem,
            ef.raiz,
            i.img_landscape_one, 
            i.img_landscape_two, 
            i.img_landscape_three
        FROM especie_forestal AS ef 
        LEFT JOIN img_species AS i ON ef.ShortcutID = i.specie_id
        WHERE ef.cod_especie = %s
        """

        # Ejecutar la consulta SQL personalizada con el parámetro 'nombre'
        with connection.cursor() as cursor:
            cursor.execute(sql_query, [code])
            results = cursor.fetchone()

         # Crear un namedtuple para manejar los datos
        fields = ["ShortcutID", "cod_especie", "nom_comunes", "otros_nombres", "nombre_cientifico", "nombre_cientifico_especie", "nombre_autor_especie", "sinonimos",
              "familia", "img_general", "distribucion", "habito", "follaje", "forma_copa", "tipo_hoja",
              "disposicion_hojas", "hojas", "img_leafs", "flor", "img_flowers", "frutos", "img_fruits", "semillas", "img_seeds",
              "tallo", "img_stem", "raiz", "img_landscape_one", "img_landscape_two", "img_landscape_three"]
        EspecieNamedTuple = namedtuple('EspecieNamedTuple', fields)

        # Convertir los resultados en un objeto namedtuple
        especie = EspecieNamedTuple(*results)

        # Crear un diccionario de los datos en el formato deseado
        formatted_result = especie._asdict()

        return Response(formatted_result)
    
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

# VISTA GLOSARIO
class GlossaryView(APIView):
    def get(self, request, format=None): 
        queryset = Glossary.objects.all()
        serializer = GlossarySerializer(queryset, many=True)

        return Response(serializer.data)

# VISTA INDIVIDUOS EVALUADOS
class GeoCandidateTreesView(APIView):
    def get(self, request, format=None): 
        # Realizar la consulta SQL
        sql_query = """
            SELECT ea.cod_especie, ea.numero_placa, ef.nom_comunes, ef.nombre_cientifico, ea.departamento, ea.municipio, ea.vereda, ea.nombre_del_predio, ea.abcisa_xy, ea.resultado 
            FROM evaluacion_as AS ea 
            INNER JOIN especie_forestal AS ef ON ea.cod_especie = ef.cod_especie
        """
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            results = cursor.fetchall()

        # Procesar los resultados
        geo_format = []
        for datos in results:
            cod_especie, numero_placa, nom_comunes, nombre_cientifico, departamento, municipio, vereda, nombre_del_predio, abcisa_xy, resultado = datos
            latitud, longitud  = abcisa_xy.split(', ')
            
            geo_fixed = {
                'codigo': int(cod_especie),
                'numero_placa': numero_placa,
                'departamento': departamento,
                'municipio': municipio,
                'vereda': vereda,
                'nombre_del_predio': nombre_del_predio,
                'lat': float(latitud),
                'lon': float(longitud),
                'coordenadas': abcisa_xy,
                'resultado': resultado,
                'nombre_comun': nom_comunes,
                'nombre_cientifico': nombre_cientifico,
            }
            geo_format.append(geo_fixed)

        return Response(geo_format)
    
class CandidatesTreesView(APIView):
    permission_classes = [IsAuthenticated]
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

                altura_ccial_str = datos['altura_fuste']
                ac = self.convert_to_decimal_or_int(altura_ccial_str)

                average_fixed = {'codigo': code_number, 'altitud': datos['altitud'], 'altura_total': at, 'altura_comercial': ac, 'cobertura': datos['cobertura']}
                average_format.append(average_fixed)

            """ print('Average data: ', average_format) """
            return Response(average_format)

        except Exception as e:
            print('Error:', str(e))
            return Response({'error': 'Ocurrió un error al obtener los datos'}, status=500)

# VISTA PÁGINA ACERCA OTROS            
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
            ea.cod_especie,
            ef.nom_comunes,
            ef.nombre_cientifico,
            COUNT(DISTINCT ea.ShortcutIDEV) AS evaluados,
            SUM(CASE WHEN mn.ShortcutIDEV IS NOT NULL THEN 1 ELSE 0 END) AS monitoreos,
            COUNT(DISTINCT mu.idmuestra) AS muestras
        FROM evaluacion_as AS ea
        LEFT JOIN especie_forestal AS ef ON ef.cod_especie = ea.cod_especie
        LEFT JOIN monitoreo AS mn ON mn.ShortcutIDEV = ea.ShortcutIDEV
        LEFT JOIN muestras AS mu ON mu.nro_placa = ea.ShortcutIDEV
        WHERE ea.numero_placa IS NOT NULL AND ea.numero_placa != ''
        GROUP BY ea.cod_especie, ef.nom_comunes, ef.nombre_cientifico;
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
            SELECT 
            ea.ShortcutIDEV, 
            ea.numero_placa, 
            ea.cod_expediente, 
            ea.cod_especie, 
            ea.fecha_evaluacion, 
            ea.departamento, 
            ea.municipio, 
            ea.altitud, 
            ea.altura_total, 
            ea.altura_fuste, 
            ea.cobertura, 
            ea.cober_otro, 
            ea.entorno_individuo, 
            ea.entorno_otro, 
            ea.especies_forestales_asociadas, 
            ea.dominancia_if, 
            ea.forma_fuste, 
            ea.dominancia, 
            ea.alt_bifurcacion, 
            ea.estado_copa, 
            ea.posicion_copa, 
            ea.fitosanitario, 
            ea.presencia, 
            ea.resultado, 
            ea.evaluacion, 
            ea.observaciones
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

class MonitoringsView(APIView):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        # Consulta SQL directa
        query = """
            SELECT
                m.IDmonitoreo,
                ea.numero_placa, 
                ef.nom_comunes, 
                ef.nombre_cientifico, 
                ea.cod_especie, 
                m.fecha_monitoreo, 
                m.hora, 
                m.temperatura, 
                m.humedad, 
                m.precipitacion, 
                m.factor_climatico, 
                m.observaciones_temp, 
                m.fitosanitario, 
                m.afectacion, 
                m.observaciones_afec,
                m.follaje_porcentaje,
                m.observaciones_follaje,
                m.flor_abierta,
                m.flor_boton,
                m.color_flor,
                m.color_flor_otro,
                m.olor_flor,
                m.olor_flor_otro,
                m.fauna_flor,
                m.fauna_flor_otros,
                m.observaciones_flor,
                m.frutos_verdes,
                m.estado_madurez,
                m.color_fruto,
                m.color_fruto_otro,
                m.medida_peso_frutos,
                m.peso_frutos,
                m.fauna_frutos,
                m.fauna_frutos_otro,
                m.observacion_frutos,
                m.cant_semillas,
                m.medida_peso_sem,
                m.peso_semillas,
                m.observacion_semilla,
                m.observaciones
            FROM 
                monitoreo AS m 
            LEFT JOIN 
                evaluacion_as AS ea ON m.ShortcutIDEV = ea.ShortcutIDEV 
            LEFT JOIN 
                especie_forestal AS ef ON ef.cod_especie = ea.cod_especie;
        """
        # Ejecutar la consulta
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        columns = [
            'IDmonitoreo', 'numero_placa', 'nom_comunes', 'nombre_cientifico',
            'cod_especie', 'fecha_monitoreo', 'hora', 'temperatura', 'humedad',
            'precipitacion', 'factor_climatico', 'observaciones_temp', 'fitosanitario',
            'afectacion', 'observaciones_afec', 'follaje_porcentaje',
            'observaciones_follaje', 'flor_abierta', 'flor_boton', 'color_flor',
            'color_flor_otro', 'olor_flor', 'olor_flor_otro', 'fauna_flor',
            'fauna_flor_otros', 'observaciones_flor', 'frutos_verdes', 'estado_madurez',
            'color_fruto', 'color_fruto_otro', 'medida_peso_frutos',
            'peso_frutos', 'fauna_frutos',
            'fauna_frutos_otro', 'observacion_frutos', 'cant_semillas',
            'medida_peso_sem', 'peso_semillas',
            'observacion_semilla', 'observaciones'
        ]
        queryset = [dict(zip(columns, row)) for row in result]

        return queryset

    def get_object(self, pk=None):
        queryset = self.get_queryset()

        if pk is not None:
            try:
                monitoring = next(monitoring for monitoring in queryset if monitoring['IDmonitoreo'] == pk)
                return monitoring
            except StopIteration:
                raise Http404
        else:
            return queryset
        
    def get_object_for_delete(self, pk):
        # Este método se utiliza específicamente para la acción de eliminación.
        try:
            return Monitoring.objects.get(pk=pk)
        except Monitoring.DoesNotExist:
            raise Http404

    def get(self, request, pk=None, format=None):
        monitorings = self.get_object(pk)

        if isinstance(monitorings, dict):
            # Convertir el resultado en una lista de diccionarios
            monitorings = [monitorings]

        return Response(monitorings)
        
# VISTA MUESTRAS
class SamplesView(APIView):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        # Consulta SQL directa
        query = """
            SELECT
                m.idmuestra, 
                ea.numero_placa, 
                ef.nom_comunes, 
                ef.nombre_cientifico, 
                ea.cod_especie, 
                m.fecha_coleccion, 
                m.nro_muestras, 
                m.colector_ppal, 
                m.siglas_colector_ppal, 
                m.nro_coleccion, 
                m.voucher, 
                m.nombres_colectores, 
                m.codigo_muestra, 
                m.otros_nombres, 
                m.descripcion, 
                m.usos 
            FROM 
                muestras AS m 
            LEFT JOIN 
                evaluacion_as AS ea ON m.nro_placa = ea.ShortcutIDEV 
            LEFT JOIN 
                especie_forestal AS ef ON ef.cod_especie = ea.cod_especie;
        """
        # Ejecutar la consulta
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        columns = [
            'idmuestra', 'numero_placa', 'nom_comunes', 'nombre_cientifico',
            'cod_especie', 'fecha_coleccion', 'nro_muestras', 'colector_ppal',
            'siglas_colector_ppal', 'nro_coleccion', 'voucher',
            'nombres_colectores', 'codigo_muestra', 'otros_nombres',
            'descripcion', 'usos'
        ]
        queryset = [dict(zip(columns, row)) for row in result]

        return queryset

    def get_object(self, pk=None):
        queryset = self.get_queryset()

        if pk is not None:
            try:
                sample = next(sample for sample in queryset if sample['idmuestra'] == pk)
                return sample
            except StopIteration:
                raise Http404
        else:
            return queryset
        
    def get_object_for_delete(self, pk):
        # Este método se utiliza específicamente para la acción de eliminación.
        try:
            return Samples.objects.get(pk=pk)
        except Samples.DoesNotExist:
            raise Http404

    def get(self, request, pk=None, format=None):
        samples = self.get_object(pk)

        if isinstance(samples, dict):
            # Convertir el resultado en una lista de diccionarios
            samples = [samples]

        return Response(samples)