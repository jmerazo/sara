import random, string
from decimal import Decimal
from django.db import connection
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination

from ..species.models import SpecieForrest
from .models import CandidatesTrees
from .serializers import CandidateTreesSerializer, CandidateTreesCreateSerializer, CandidatesSpecieForrestSerializer

def convert_to_decimal_or_int(value):
    if value is None or value == '':
        return None
    try:
        return Decimal(value)
    except (TypeError, ValueError):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
        
def convert_to_decimal(value):
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except (TypeError, ValueError):
        return None

def convert_to_float(value):
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def generate_random_id(length):
            characters = string.ascii_letters + string.digits
            random_id = ''.join(random.choice(characters) for _ in range(length))
            return random_id

# VISTA INDIVIDUOS EVALUADOS    
class GeoCandidateTreesView(APIView):
    def get(self, request, format=None):
        with connection.cursor() as cursor:
            try:
                # Consulta SQL para unir los datos de SARA, GBIF y SISA
                cursor.execute("""
                    SELECT 
                        ef.code_specie AS codigo, 
                        ea.numero_placa, 
                        dp.name AS departamento,
                        pr.p_departamento_id, 
                        ct.name AS municipio,
                        pr.p_municipio_id, 
                        ea.locality AS vereda, 
                        pr.nombre_predio, 
                        ea.abcisa_xy AS coordenadas, 
                        ef.vernacularName AS nombre_comun,
                        ef.nombre_cientifico AS nombre_cientifico,
                        ef.taxon_key, 
                        ef.habit AS habito,
                        ea.evaluacion,
                        'original' AS source,
                        SUBSTRING_INDEX(ea.abcisa_xy, ', ', 1) AS lat, 
                        SUBSTRING_INDEX(ea.abcisa_xy, ', ', -1) AS lon
                    FROM 
                        evaluacion_as_c ea
                    JOIN 
                        especie_forestal_c ef ON ef.code_specie = ea.cod_especie_id
                    JOIN 
                        predios pr ON pr.id = ea.property_id
                    JOIN 
                        departments dp ON dp.id = pr.p_departamento_id
                    JOIN
                        cities ct ON ct.id = pr.p_municipio_id 
                    WHERE 
                        ea.numero_placa IS NOT NULL 
                        AND ea.abcisa_xy IS NOT NULL

                    UNION ALL

                    SELECT 
                        ef.code_specie AS codigo,  
                        NULL AS numero_placa, 
                        NULL AS departamento,
                        NULL AS p_departamento_id, 
                        NULL AS municipio,
                        NULL AS p_municipio_id, 
                        NULL AS vereda, 
                        NULL AS nombre_del_predio, 
                        CONCAT(gb.decimalLatitude, ', ', gb.decimalLongitude) AS coordenadas, 
                        gb.vernacularName AS nombre_comun,
                        gb.scientificName,
                        gb.taxonKey, 
                        ef.habit AS habito,
                        NULL as evaluacion,
                        'gbif' AS source,
                        gb.decimalLatitude AS lat, 
                        gb.decimalLongitude AS lon
                    FROM 
                        gbif_species gb
                    LEFT JOIN 
                        especie_forestal_c ef ON gb.taxonKey = ef.taxon_key
                    WHERE 
                        gb.taxonKey IS NOT NULL

                    UNION ALL

                    SELECT
                        s.code_specie AS codigo,
                        NULL AS numero_placa,
                        dp.name AS departamento,
                        s.department_id AS p_departamento_id,
                        ct.name AS municipio,
                        s.city_id AS p_municipio_id,
                        NULL AS vereda,
                        NULL AS nombre_predio,
                        CONCAT(s.lat, ', ', s.long) AS coordenadas,
                        s.vernacularName AS nombre_comun,
                        s.scientificName,
                        NULL AS taxon_key,
                        ef.habit AS habito,
                        NULL AS evaluacion,
                        s.source,
                        s.lat,
                        s.long AS lon
                    FROM 
                        sisa s
                    LEFT JOIN
                        departments dp ON dp.id = s.department_id
                    LEFT JOIN 
                        especie_forestal_c ef ON ef.code_specie = s.code_specie
                    LEFT JOIN
                        cities ct ON ct.id = s.city_id
                    WHERE
                        s.lat IS NOT NULL
                        AND s.long IS NOT NULL;
                """)
                # Obtener todos los resultados
                geo_format = cursor.fetchall()

                if not geo_format:
                    return Response({"message": "No se encontraron resultados"}, status=status.HTTP_200_OK)

                # Definir las columnas que corresponden a cada campo
                columns = [
                    'codigo', 'numero_placa', 'departamento', 'departamento_id', 'municipio', 'municipio_id', 'vereda', 'nombre_del_predio',
                    'coordenadas', 'nombre_comun', 'nombre_cientifico', 'taxon_key', 'habito', 'evaluacion', 'source', 'lat', 'lon'
                ]

                # Convertir los resultados en una lista de diccionarios
                geo_format_dict = [dict(zip(columns, row)) for row in geo_format]

                return Response(geo_format_dict, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CandidatesTreesView(APIView):
    def get(self, request, np=None, format=None): 
        if np:
            queryset = CandidatesTrees.objects.filter(id=np).prefetch_related('cod_especie', 'user', 'property')
        else:
            queryset = CandidatesTrees.objects.exclude(numero_placa__isnull=True).prefetch_related('cod_especie', 'user', 'property')
        
        # Serializar los datos obtenidos
        serializer = CandidateTreesSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = CandidateTreesCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, np, format=None):
        tree = get_object_or_404(CandidatesTrees, numero_placa=np)
        serializer = CandidateTreesCreateSerializer(tree, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, np, format=None):
        tree = get_object_or_404(CandidatesTrees, pk=np)
        tree.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AverageCandidateTreesView(APIView):
    def get(self, request, format=None):
        try:
            # Utilizar values() para obtener solo los campos necesarios
            average = CandidatesTrees.objects.exclude(numero_placa__isnull=True).values(
                'cod_especie', 'altitud', 'altura_total', 'altura_fuste', 'cobertura'
            )

            average_format = []

            for datos in average:
                code_number = datos['cod_especie']
                altura_total_str = datos.get('altura_total', None)
                at = convert_to_decimal_or_int(altura_total_str)
                altura_ccial_str = datos.get('altura_fuste', None)
                ac = convert_to_decimal_or_int(altura_ccial_str)
                average_fixed = {
                    'codigo': code_number,
                    'altitud': datos.get('altitud', None),
                    'altura_total': at,
                    'altura_comercial': ac,
                    'cobertura': datos.get('cobertura', None)
                }
                average_format.append(average_fixed)

            return Response(average_format)

        except Exception as e:
            print('Error:', str(e))
            return Response({'error': 'Ocurrió un error al obtener los datos'}, status=500)

class SearchCandidatesSpecieView(APIView):
    def get(self, request, code, format=None):
        sql = """
            SELECT 
                ea.id,
                ea.eventDate,
                ea.numero_placa,
                ea.cod_expediente,
                ea.cod_especie_id,
                ea.property_id,
                ea.minimumElevationInMeters,
                ea.cobertura,
                ea.entorno_individuo,
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
                ea.observaciones,
                ef.habit,
                ef.vernacularName,
                ef.nombre_cientifico,
                p.p_departamento_id,
                dp.name AS departamento_name,
                ct.name AS ciudad_name,
                p.p_municipio_id,
                p.p_user_id
            FROM 
                evaluacion_as_c AS ea
            INNER JOIN 
                especie_forestal_c AS ef ON ea.cod_especie_id = ef.code_specie
            LEFT JOIN 
                predios AS p ON ea.property_id = p.id
            INNER JOIN 
                departments AS dp ON p.p_departamento_id = dp.id
            INNER JOIN 
                cities AS ct ON p.p_municipio_id = ct.id
            WHERE 
                ef.code_specie = %s
            AND 
                ea.numero_placa IS NOT NULL
            AND ea.estado_placa <> 'Archivado';
        """
        
        with connection.cursor() as cursor:
            cursor.execute(sql, [code])
            result = cursor.fetchall()
            
            # Verifica si cursor.description y result tienen datos
            if cursor.description and result:
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in result]
            else:
                data = []  # Asigna una lista vacía si no hay resultados

        return Response({
            'success': True,
            'message': 'Consulta realizada con éxito',
            'data': data
        })
        
class CandidatesSpecieUserView(APIView):
    def get(self, request, user_id, format=None):
        # Realiza la consulta utilizando el ORM de Django
        queryset = CandidatesTrees.objects.filter(
            user=user_id, 
            numero_placa__isnull=False
        ).select_related('cod_especie').values()

        # Convierte el queryset a una lista de diccionarios
        data = list(queryset)

        return Response(data)