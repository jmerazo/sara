from rest_framework import status
from collections import namedtuple
from django.db import connection, transaction
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.views import APIView
from django.db.models import Count, Sum, Case, When, IntegerField, Q
from django.db.models import Prefetch
from django.db import connection
import random, string, os, base64

from ..candidates.models import CandidatesTrees
from .models import SpecieForrest, ImageSpeciesRelated, Families
from .serializers import SpecieForrestSerializer

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
class SpecieForrestView(APIView):
    def get_object(self, pk=None):
        if pk is not None:
            try:
                return SpecieForrest.objects.get(ShortcutID=pk)
            except SpecieForrest.DoesNotExist:
                raise Http404
        else:
            return SpecieForrest.objects.all()

    def get(self, request, pk=None, format=None):
        if pk is not None:
            species = get_object_or_404(SpecieForrest, pk=pk)
            serializer = SpecieForrestSerializer(species)
            return Response(serializer.data)
        else:
            species_list = SpecieForrest.objects.prefetch_related('images').all()
            serializer = SpecieForrestSerializer(species_list, many=True)
            return Response(serializer.data)   
    
    @transaction.atomic
    def post(self, request, format=None):
        adjusted_data = request.data.copy()

        ce = adjusted_data.get('cod_especie')

        existing_specie = SpecieForrest.objects.filter(cod_especie=ce).first()
        if existing_specie:
            return Response({'error': f'El código de especie {ce} ya está registrado en otra especie.'}, status=status.HTTP_400_BAD_REQUEST)

        while True:
            random_id = generate_random_id(8)
            existing_code = SpecieForrest.objects.filter(ShortcutID=random_id).first()
            
            if existing_code is None:
                # El ID no existe en la base de datos, se puede utilizar
                break

        cod_especie_img = adjusted_data['cod_especie']

        base_dir = 'images'
        sub_dir = os.path.join(base_dir, cod_especie_img)
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

        img_related = ImageSpeciesRelated()
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

        img_related = ImageSpeciesRelated()
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

        serializer = SpecieForrestSerializer(data=adjusted_data)
        if serializer.is_valid():
            specie = SpecieForrest(
                ShortcutID = random_id,
                cod_especie = adjusted_data['cod_especie'],
                nom_comunes = adjusted_data['nom_comunes'],
                otros_nombres = adjusted_data['otros_nombres'],
                nombre_cientifico = adjusted_data['nombre_cientifico'],
                sinonimos = adjusted_data['sinonimos'],
                familia = adjusted_data['familia'],
                distribucion = adjusted_data['distribucion'],
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
        specie = get_object_or_404(SpecieForrest, ShortcutID=pk)
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
        hojas = adjusted_data.get('hojas')
        flor = adjusted_data.get('flor')
        frutos = adjusted_data.get('frutos')
        semillas = adjusted_data.get('semillas')
        tallo = adjusted_data.get('tallo')
        raiz = adjusted_data.get('raiz')
        
        # Asegurémonos de que el nuevo email o número de documento no existan en otros usuarios
        if cod_specie_currently != cod_especie_new:
            existing_specie = SpecieForrest.objects.exclude(ShortcutID=pk).filter(cod_especie=cod_especie_new).first()
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
        specie.hojas = hojas
        specie.flor = flor
        specie.frutos = frutos
        specie.semillas = semillas
        specie.tallo = tallo
        specie.raiz = raiz        

        # Aquí debes continuar actualizando los demás campos según tus necesidades

        specie.save()  # Guardar los cambios

        serializer = SpecieForrestSerializer(specie)  # Serializa el usuario actualizado
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        specie = self.get_object(pk)
        specie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SearchSpecieForrestView(APIView):
    def get(self, request, code, format=None):
        # Obtener la especie con sus imágenes relacionadas
        specie = get_object_or_404(SpecieForrest.objects.prefetch_related('images'), code_specie=code)
        
        # Serializar los datos de la especie
        serializer = SpecieForrestSerializer(specie)
        
        return Response(serializer.data)
    
class SearchFamilyView(APIView):
    def get(self, request, family, format=None):        
        search = SpecieForrest.objects.filter(familia__icontains=family)
        serializer = SpecieForrestSerializer(search, many=True)
        
        return Response(serializer.data)

class FamiliesView(APIView):
    def get(self, request, format=None):
        # Obtener todas las familias con solo los campos necesarios
        familias = Families.objects.all().only('name', 'description')

        resultado = []

        # Crear un diccionario para cachear las especies por familia
        especies_dict = {}
        especies = SpecieForrest.objects.all().only('vernacularName', 'family')
        for especie in especies:
            familia_nombre = especie.family
            if familia_nombre not in especies_dict:
                especies_dict[familia_nombre] = []
            especies_dict[familia_nombre].append(especie.vernacularName)

        # Recorrer las familias
        for familia in familias:
            familia_nombre = familia.name
            description = familia.description

            # Obtener las especies relacionadas a la familia actual desde el diccionario cacheado
            especies_nombres = especies_dict.get(familia_nombre, [])

            # Agregar la familia y las especies a la lista de resultados
            resultado.append({
                'familia': familia_nombre,
                'description': description,
                'especies': especies_nombres
            })

        return Response(resultado)

class ReportSpecieDataView(APIView):
    def get(self, request, format=None):
        query = """
        SELECT
            ea.cod_especie_id,
            ef.vernacularName,
            ef.nombre_cientifico,
            COUNT(DISTINCT CASE WHEN ea.estado_placa <> 'Archivado' THEN ea.id ELSE NULL END) AS evaluados,
            SUM(CASE WHEN mn.id IS NOT NULL THEN 1 ELSE 0 END) AS monitoreos,
            COUNT(DISTINCT mu.id) AS muestras
        FROM evaluacion_as_c AS ea
        LEFT JOIN especie_forestal_c AS ef ON ef.code_specie = ea.cod_especie_id
        LEFT JOIN monitoreo_c AS mn ON mn.id = ea.id
        LEFT JOIN muestras_c AS mu ON mu.evaluacion_id = ea.id
        WHERE ea.numero_placa IS NOT NULL
        GROUP BY ea.cod_especie_id, ef.vernacularName, ef.nombre_cientifico;
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
                'evaluados': int(row[3]),
                'monitoreos': int(row[4]),
                'muestras': int(row[5]),
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
            ea.cod_especie_id, 
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
            INNER JOIN especie_forestal AS ef ON ea.cod_especie_id = ef.cod_especie
            WHERE ef.nom_comunes = '%s' AND ea.numero_placa IS NOT NULL;
        """

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