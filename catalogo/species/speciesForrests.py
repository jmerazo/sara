import os
import json
from django.db import models
from django.db import connection
from rest_framework import status
from django.core.cache import cache
from rest_framework.views import APIView
import random, string, os, base64, shutil
from rest_framework.response import Response
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from ..helpers.pdfToImages import pdf_to_images

from .models import SpecieForrest, ImageSpeciesRelated, Families, SpeciesGBIF
from .serializers import SpecieForrestSerializer, SpecieForrestCreatSerializer, SpecieForrestCreateSerializer, SpeciesGBIFSerializer

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

# VISTAS ESPECIES FORESTALES
class SpecieForrestView(APIView):
    def get_object(self, pk=None):
        if pk is not None:
            try:
                return SpecieForrest.objects.get(id=pk)
            except SpecieForrest.DoesNotExist:
                raise Http404
        else:
            return SpecieForrest.objects.all()

    def get(self, request, pk=None, format=None):
        exclude_codes = [
            2020, 1897, 2838, 4211, 1747, 5377, 2843, 120, 2320, 2323, 1786, 2484, 2789, 3172, 
            3434, 4449, 2768, 5392, 5284, 5309, 179, 9994, 9992, 9989, 146, 9988, 4803, 1348, 
            206, 4946, 5290, 9986, 9982, 142, 2093
        ]
        cache.set('exclude_codes', exclude_codes, timeout=3600)
        
        if pk is not None:
            species = get_object_or_404(SpecieForrest, pk=pk)
            serializer = SpecieForrestSerializer(species)
            return Response(serializer.data)
        else:
            # Excluir los objetos con code_specie en la lista exclude_codes
            species_list = SpecieForrest.objects.prefetch_related('images').exclude(code_specie__in=exclude_codes)
            serializer = SpecieForrestSerializer(species_list, many=True)
            return Response(serializer.data)
    
    def post(self, request, format=None):
        adjusted_data = request.data.copy()

        # Manejo de imágenes
        cod_especie_img = adjusted_data['code_specie']

        base_dir = 'images'
        sub_dir = os.path.join(base_dir, cod_especie_img)
        os.makedirs(sub_dir, exist_ok=True)  # Asegura que la carpeta principal exista

        image_fields = {
            'img_general': 'imageInputGeneral',
            'img_leafs': 'imageInputLeaf',
            'img_flowers': 'imageInputFlower',
            'img_fruits': 'imageInputFruit',
            'img_seeds': 'imageInputSeed',
            'img_stem': 'imageInputStem',
            'img_landscape_one': 'imageInputLandScapeOne',
            'img_landscape_two': 'imageInputLandScapeTwo',
            'img_landscape_three': 'imageInputLandScapeThree',
        }

        # Función para generar un nombre de archivo aleatorio
        def generate_random_filename(length):
            characters = string.ascii_letters + string.digits
            return ''.join(random.choice(characters) for _ in range(length))

        img_related_data = {}

        for field_name, input_name in image_fields.items():
            img_data = adjusted_data.get(input_name)
            if img_data:
                random_filename = generate_random_filename(8)
                file_extension = ".jpeg"  # Reemplaza con la extensión de archivo adecuada

                destination_path = os.path.join(sub_dir, f"{input_name}_{random_filename}{file_extension}")

                img_data = img_data.split(';base64,')[-1]
                img_data_bytes = base64.b64decode(img_data)

                with open(destination_path, 'wb') as dest_file:
                    dest_file.write(img_data_bytes)

                img_related_data[field_name] = destination_path

        # Ahora, utiliza el serializer
        serializer = SpecieForrestCreatSerializer(data=adjusted_data)
        if serializer.is_valid():
            specie = serializer.save()  # Guarda la instancia de SpecieForrest
            # Guarda la relación de imágenes
            if img_related_data:
                img_related = ImageSpeciesRelated.objects.create(specie=specie, **img_related_data)
                img_related.save()

            return Response({
                'success': True,
                'message': 'Especie creada con éxito!',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Error al crear la especie',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        specie = get_object_or_404(SpecieForrest, id=pk)
        adjusted_data = request.data

        code_specie_currently = specie.code_specie
        code_specie_new = adjusted_data.get('code_specie')

        # Validar si el nuevo código de especie ya está en uso
        if code_specie_currently != code_specie_new:
            existing_specie = SpecieForrest.objects.exclude(id=pk).filter(cod_especie=code_specie_new).first()
            if existing_specie:
                return Response({'error': f'El código de especie {code_specie_new} ya está registrado en otra especie.'}, status=status.HTTP_400_BAD_REQUEST)

        cod_especie_img = adjusted_data['code_specie']
        base_dir = 'images'
        sub_dir = os.path.join(base_dir, cod_especie_img)
        os.makedirs(sub_dir, exist_ok=True)  # Asegúrate de que la carpeta exista

        # Obtener los datos de las imágenes del request
        imgGeneral = adjusted_data.get('imageInputGeneral')
        imgLeaf = adjusted_data.get('imageInputLeaf')
        imgFlower = adjusted_data.get('imageInputFlower')
        imgFruit = adjusted_data.get('imageInputFruit')
        imgSeed = adjusted_data.get('imageInputSeed')
        imgStem = adjusted_data.get('imageInputStem')
        imgLandScapeOne = adjusted_data.get('imageInputLandScapeOne')
        imgLandScapeTwo = adjusted_data.get('imageInputLandScapeTwo')
        imgLandScapeThree = adjusted_data.get('imageInputLandScapeThree')

        # Crear diccionario con las imágenes
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

        # Nombres válidos de imágenes para el guardado
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

        # Función para generar un nombre aleatorio para los archivos
        def generate_random_filename(length):
            characters = string.ascii_letters + string.digits
            return ''.join(random.choice(characters) for _ in range(length))

        # Actualizar imágenes
        for column_name, img_data in image_columns.items():
            if img_data:
                random_filename = generate_random_filename(8)
                file_extension = ".jpeg"  # Reemplaza con la extensión correcta si es necesario

                valid_image_name = valid_image_names[column_name]
                destination_path = os.path.join(sub_dir, f"{valid_image_name}_{random_filename}{file_extension}")

                img_data = img_data.split(';base64,')[-1]
                img_data_bytes = base64.b64decode(img_data)

                # Guardar la imagen en la carpeta correspondiente
                with open(destination_path, 'wb') as dest_file:
                    dest_file.write(img_data_bytes)

                # Asignar la ruta de la imagen al campo correspondiente del modelo
                setattr(specie, column_name, destination_path)
                print(f"Imagen actualizada en {column_name}")

        # Usar el serializer para validar y actualizar otros campos
        serializer = SpecieForrestCreateSerializer(specie, data=adjusted_data)
        if serializer.is_valid():
            serializer.save()  # Guardar cambios en el modelo SpecieForrest
            return Response({
                'success': True,
                'message': 'Especie actualizada con éxito!',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Error al actualizar la especie',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        try:
            # Obtener la especie
            specie = self.get_object(pk)

            # Obtener las imágenes relacionadas
            img_related_qs = ImageSpeciesRelated.objects.filter(specie=specie)

            if img_related_qs.exists():
                for img_related in img_related_qs:
                    # Obtener todos los campos que son CharField y pueden contener rutas de imágenes
                    fields = [field.name for field in img_related._meta.get_fields() if isinstance(field, models.CharField)]

                    for field_name in fields:
                        image_path = getattr(img_related, field_name)
                        if image_path and os.path.exists(image_path):
                            try:
                                os.remove(image_path)
                            except Exception as e:
                                print(f"Error al eliminar la imagen {image_path}: {e}")

                # Eliminar registros de imágenes relacionadas
                img_related_qs.delete()

            # Eliminar el directorio de imágenes asociado
            # Asumimos que el directorio está nombrado por el código de especie
            base_dir = 'images'
            specie_code = specie.code_specie  # Asegúrate de que 'code_specie' es el nombre correcto del campo
            dir_to_remove = os.path.join(base_dir, str(specie_code))

            if os.path.exists(dir_to_remove) and os.path.isdir(dir_to_remove):
                try:
                    shutil.rmtree(dir_to_remove)
                except Exception as e:
                    print(f"Error al eliminar el directorio {dir_to_remove}: {e}")

            # Eliminar la especie
            specie.delete()

            # Retornar respuesta exitosa
            return Response({
                'success': True,
                'message': 'Especie eliminada con éxito!',
                'data': None
            }, status=status.HTTP_200_OK)

        except SpecieForrest.DoesNotExist:
            return Response({
                'success': False,
                'message': 'La especie no existe.',
                'errors': {'specie': ['No se encontró la especie especificada.']}
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error al eliminar la especie',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)

class SearchSpecieForrestView(APIView):
    def get(self, request, code, format=None):
        print('code search ', code)
        with connection.cursor() as cursor:
            # Consulta para la especie y las imágenes relacionadas
            cursor.execute("""
                SELECT 
                    ef.id,
                    ef.taxon_key,
                    ef.code_specie, 
                    ef.vernacularName, 
                    ef.scientificName, 
                    ef.scientificNameAuthorship,
                    ef.family, 
                    ef.genus, 
                    ef.descriptionGeneral, 
                    ef.leaves, 
                    ef.flowers, 
                    ef.fruits, 
                    ef.seeds,

                    -- JSON Array de Imágenes Relacionadas
                    (SELECT 
                        JSON_ARRAYAGG(
                            JSON_OBJECT(
                                'img_general', img.img_general,
                                'img_leafs', img.img_leafs,
                                'img_fruits', img.img_fruits,
                                'img_flowers', img.img_flowers,
                                'img_seeds', img.img_seeds,
                                'img_stem', img.img_stem,
                                'img_landscape_one', img.img_landscape_one,
                                'img_landscape_two', img.img_landscape_two,
                                'img_landscape_three', img.img_landscape_three,
                                'protocol', img.protocol,
                                'resolution_protocol', img.resolution_protocol,
                                'annex_one', img.annex_one,
                                'annex_two', img.annex_two,
                                'format_coordinates', img.format_coordinates,
                                'intructive_coordinates', img.intructive_coordinates,
                                'format_inventary', img.format_inventary
                            )
                        )
                    FROM img_species img 
                    WHERE img.specie_id = ef.id) AS images
                FROM 
                    especie_forestal_c ef
                WHERE 
                    ef.code_specie = %s
                GROUP BY 
                    ef.id, ef.taxon_key, ef.code_specie, ef.vernacularName, ef.scientificName, ef.family, 
                    ef.genus, ef.descriptionGeneral, ef.leaves, ef.flowers, ef.fruits, ef.seeds;
            """, [code])
            specie_result = cursor.fetchone()

            if specie_result:
                # Consulta para los datos de evaluacion_as_c
                cursor.execute("""
                    SELECT 
                        SUBSTRING_INDEX(ea.abcisa_xy, ', ', 1) AS lat,
                        SUBSTRING_INDEX(ea.abcisa_xy, ', ', -1) AS lon,
                        ef.habit AS habito,
                        ea.created AS last_created,
                        'original' AS source
                    FROM evaluacion_as_c ea
                    LEFT JOIN especie_forestal_c ef ON ea.cod_especie_id = ef.code_specie
                    WHERE ef.code_specie = %s AND ea.numero_placa IS NOT NULL
                """, [code])
                geo_data_original = cursor.fetchall()

                # Consulta para los datos de gbif_species
                cursor.execute("""
                    SELECT 
                        gb.decimalLatitude AS lat,
                        gb.decimalLongitude AS lon,
                        ef.habit AS habito,
                        gb.created AS last_created,
                        'gbif' AS source
                    FROM gbif_species gb
                    LEFT JOIN especie_forestal_c ef ON gb.taxonKey = ef.taxon_key
                    WHERE ef.code_specie = %s
                """, [code])
                geo_data_gbif = cursor.fetchall()

                # Consulta para los datos de sisa
                cursor.execute("""
                    SELECT 
                        s.lat,
                        s.long AS lon,
                        ef.habit AS habito,
                        NULL AS last_created,
                        s.source
                    FROM sisa s
                    LEFT JOIN especie_forestal_c ef ON s.code_specie = ef.code_specie
                    WHERE ef.code_specie = %s
                """, [code])
                geo_data_sisa = cursor.fetchall()

                # Combinar los datos en geo_data
                geo_data = [
                    {'lat': row[0], 'lon': row[1], 'habito': row[2], 'last_created': row[3], 'source': row[4]}
                    for result in [geo_data_original, geo_data_gbif, geo_data_sisa]
                    for row in result
                ]

                # Manejar imágenes (si existen)
                images_data = specie_result[13]
                images = json.loads(images_data) if images_data is not None else []

                protocol_path = None

                # Verificar si hay protocolo en las imágenes
                if images:
                    protocol_path = images[0].get('protocol', None)

                if protocol_path:
                    # Convertir los separadores de Windows (\) a Linux (/)
                    protocol_path = protocol_path.replace("\\", "/")

                    # Crear la ruta del directorio flipbook
                    base_dir = os.path.dirname(protocol_path)
                    flipbook_dir = os.path.join(base_dir, "flipbook")

                    num_pages = 0  # Inicializar num_pages como 0 por defecto

                    # Convertir las rutas de directorios a formato compatible
                    base_dir = base_dir.replace("\\", "/")
                    flipbook_dir = flipbook_dir.replace("\\", "/")

                    if not os.path.exists(flipbook_dir):
                        os.makedirs(flipbook_dir)
                        # Convertir el PDF a imágenes y guardarlas en flipbook_dir
                        pdf_to_images(protocol_path, flipbook_dir)

                    # Contar los archivos .jpg en el directorio flipbook si este existe
                    if os.path.exists(flipbook_dir):
                        num_pages = len([
                            file for file in os.listdir(flipbook_dir)
                            if file.lower().endswith('.jpg')  # Manejar extensiones en mayúsculas/minúsculas
                        ])
                else:
                    num_pages = None  # O usar 0 si prefieres que el valor sea numérico

                # Construir la respuesta
                response_data = {
                    'id': specie_result[0],
                    'taxon_key': specie_result[1],
                    'code_specie': specie_result[2],
                    'vernacularName': specie_result[3],
                    'scientificName': specie_result[4],
                    'scientificNameAuthorship': specie_result[5],  # Nuevo campo agregado
                    'family': specie_result[6],
                    'genus': specie_result[7],
                    'descriptionGeneral': specie_result[8],
                    'leaves': specie_result[9],
                    'flowers': specie_result[10],
                    'fruits': specie_result[11],
                    'seeds': specie_result[12],
                    'images': images,
                    'geo_data': geo_data,
                    'num_pages': num_pages,  # Agregado correctamente
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Especie no encontrada"}, status=status.HTTP_404_NOT_FOUND)
            
class SearchFamilyView(APIView):
    def get(self, request, family, format=None):        
        search = SpecieForrest.objects.filter(family__icontains=family)
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
    
class SpecieGBIFView(APIView):
    def post(self, request, format=None):
        data = request.data

        if not isinstance(data, list):
            return Response({"error": "Se espera una lista de ocurrencias"}, status=status.HTTP_400_BAD_REQUEST)

        results = []
        errors = []
        new_entries = []

        for item in data:
            gbifID = item.get('gbifID')
            if not gbifID:
                errors.append({"error": "Falta el gbifID en los datos de la ocurrencia"})
                continue

            # Verificar si el registro ya existe
            if SpeciesGBIF.objects.filter(gbifID=gbifID).exists():
                results.append(f"El registro con gbifID {gbifID} ya existe.")
                continue

            new_entry = SpeciesGBIF(
                gbifID=gbifID,
                taxonKey=item.get('taxonKey'),
                vernacularName=item.get('vernacularName'),
                scientificName=item.get('scientificName'),
                decimalLatitude=item.get('decimalLatitude'),
                decimalLongitude=item.get('decimalLongitude'),
                basisOfRecord=item.get('basisOfRecord'),
                institutionCode=item.get('institutionCode'),
                collectionCode=item.get('collectionCode'),
                catalogNumber=item.get('catalogNumber'),
                recordedBy=item.get('recordedBy'),
                elevation=item.get('elevation')
            )
            new_entries.append(new_entry)

        try:
            if new_entries:
                SpeciesGBIF.objects.bulk_create(new_entries, batch_size=1000)
                results.append(f"{len(new_entries)} nuevos registros almacenados exitosamente.")
            else:
                results.append("No hay nuevos datos para almacenar.")
        except Exception as e:
            errors.append({"error": str(e)})

        response_data = {"results": results, "errors": errors}
        return Response(response_data, status=status.HTTP_200_OK)
    
class SpecieGBIFExistsView(APIView):
    def get(self, request, taxonKey, format=None):
        exists = SpeciesGBIF.objects.filter(taxonKey=taxonKey).exists()
        return Response({'exists': exists}, status=status.HTTP_200_OK)
