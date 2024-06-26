from rest_framework import viewsets, status
from collections import namedtuple
from django.db import connection, transaction
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.views import APIView
from django.db.models import Count
from django.db import connection
import random, string, os, base64
from .models import specieForrest, ImageSpeciesRelated, Families
from .serializers import EspecieForestalSerializer,NombresComunesSerializer, FamilySerializer, FamiliaSerializer, NombreCientificoSerializer
from rest_framework.permissions import IsAuthenticated

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
                return specieForrest.objects.get(ShortcutID=pk)
            except specieForrest.DoesNotExist:
                raise Http404
        else:
            return specieForrest.objects.all()

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

        existing_specie = specieForrest.objects.filter(cod_especie=ce).first()
        if existing_specie:
            return Response({'error': f'El código de especie {ce} ya está registrado en otra especie.'}, status=status.HTTP_400_BAD_REQUEST)

        while True:
            random_id = generate_random_id(8)
            existing_code = specieForrest.objects.filter(ShortcutID=random_id).first()
            
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

        serializer = EspecieForestalSerializer(data=adjusted_data)
        if serializer.is_valid():
            specie = specieForrest(
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
        specie = get_object_or_404(specieForrest, ShortcutID=pk)
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
            existing_specie = specieForrest.objects.exclude(ShortcutID=pk).filter(cod_especie=cod_especie_new).first()
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

        serializer = EspecieForestalSerializer(specie)  # Serializa el usuario actualizado
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        specie = self.get_object(pk)
        specie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class NombresComunesView(viewsets.ModelViewSet):
   queryset = specieForrest.objects.all()
   serializer_class = NombresComunesSerializer

class FamiliaView(APIView):
    serializer_class = FamiliaSerializer

    def get(self, request, format=None):
        queryset = specieForrest.objects.values('familia').distinct()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

class NombreCientificoView(viewsets.ModelViewSet):
   queryset = specieForrest.objects.all()
   serializer_class = NombreCientificoSerializer

class SuggestionTypeView(APIView):
    def get(self, request, types, format=None):
        if types == 'familia':
            queryset = specieForrest.objects.values_list('familia', flat=True)
        elif types == 'nom_comunes':
            queryset = specieForrest.objects.values_list('nom_comunes', flat=True)
        elif types == 'nombre_cientifico':
            queryset = specieForrest.objects.values_list('nombre_cientifico', flat=True)
        else:
            queryset = []

        return Response(list(queryset))

suggestion_type_view = SuggestionTypeView.as_view()

class BuscarEspeciezView(APIView):
    def get(self, request, nombre, format=None):        
        search = specieForrest.objects.filter(nom_comunes__icontains=nombre).first()
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
            ef.distribucion,
            i.img_general,
            ef.descripcion_general,
            ef.hojas,
            i.img_leafs,
            ef.flor,
            i.img_flowers,
            ef.frutos,
            i.img_fruits,
            ef.semillas,
            i.img_seeds,
            ef.usos_maderables,            
            ef.usos_no_maderables,
            i.img_stem,
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
              "familia", "distribucion", "img_general", "descripcion_general", "hojas", "img_leafs", "flor", "img_flowers", "frutos", "img_fruits", "semillas", "img_seeds",
              "usos_maderables", "usos_no_maderables", "img_stem", "img_landscape_one", "img_landscape_two", "img_landscape_three"]
        EspecieNamedTuple = namedtuple('EspecieNamedTuple', fields)

        # Convertir los resultados en un objeto namedtuple
        especie = EspecieNamedTuple(*results)

        # Crear un diccionario de los datos en el formato deseado
        formatted_result = especie._asdict()

        return Response(formatted_result)
    
class BuscarFamiliaView(APIView):
    def get(self, request, family, format=None):        
        search = specieForrest.objects.filter(familia__icontains=family)
        serializer = EspecieForestalSerializer(search, many=True)
        
        return Response(serializer.data)

class FamiliesView(APIView):
    def get(self, request, format=None):
        # Obtener las familias
        #familias = specieForrest.objects.values('familia').annotate(total=Count('familia')).distinct()
        familias = Families.objects.all().only('name', 'description')

        resultado = []

        # Recorrer las familias
        for familia in familias:
            familia_nombre = familia.name
            description = familia.description

            # Obtener las especies relacionadas a la familia actual
            especies = specieForrest.objects.filter(familia=familia_nombre)

            # Crear una lista de nombres de especies
            especies_nombres = [especie.nom_comunes for especie in especies]

            # Agregar la familia y las especies a la lista de resultados
            resultado.append({
                'familia': familia_nombre,
                'description' : description,
                'especies': especies_nombres
            })

        return Response(resultado)
    
class ScientificNameView(APIView):
    def get(self, request, scientific, format=None):        
        search = specieForrest.objects.filter(nombre_cientifico__icontains=scientific).first()
        serializer = EspecieForestalSerializer(search)
        
        return Response(serializer.data)

class ReportSpecieDataView(APIView):
    def get(self, request, format=None):
        query = """
        SELECT
            ea.cod_especie,
            ef.nom_comunes,
            ef.nombre_cientifico,
            COUNT(DISTINCT CASE WHEN ea.estado_placa <> 'Archivado' THEN ea.ShortcutIDEV ELSE NULL END) AS evaluados,
            SUM(CASE WHEN mn.ShortcutIDEV IS NOT NULL THEN 1 ELSE 0 END) AS monitoreos,
            COUNT(DISTINCT mu.idmuestra) AS muestras
        FROM evaluacion_as AS ea
        LEFT JOIN especie_forestal AS ef ON ef.cod_especie = ea.cod_especie
        LEFT JOIN monitoreo AS mn ON mn.ShortcutIDEV = ea.ShortcutIDEV
        LEFT JOIN muestras AS mu ON mu.nro_placa = ea.ShortcutIDEV
        WHERE ea.numero_placa IS NOT NULL
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