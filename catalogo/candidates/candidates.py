from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection
from decimal import Decimal
import random, string
from .models import CandidatesTrees
from .serializers import CandidateTreesSerializer, AverageTreesSerializer
from rest_framework.permissions import IsAuthenticated

def generate_random_id(length):
            characters = string.ascii_letters + string.digits
            random_id = ''.join(random.choice(characters) for _ in range(length))
            return random_id

# VISTA INDIVIDUOS EVALUADOS    
class GeoCandidateTreesView(APIView):
    def get(self, request, format=None): 
        # Realizar la consulta SQL
        sql_query = """
            SELECT ea.cod_especie, ea.numero_placa, ef.nom_comunes, ef.nombre_cientifico, ea.departamento, ea.municipio, ea.vereda, ea.nombre_del_predio, ea.abcisa_xy, ea.resultado 
            FROM evaluacion_as AS ea 
            INNER JOIN especie_forestal AS ef ON ea.cod_especie = ef.cod_especie
            WHERE ea.numero_placa IS NOT NULL
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
    def get(self, request, pk=None, format=None): 
        if pk:
            # Obtener un objeto específico por pk
            queryset = CandidatesTrees.objects.filter(ShortcutIDEV=pk)
        else:
            queryset = CandidatesTrees.objects.exclude(numero_placa__isnull=True)

        serializer = CandidateTreesSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = CandidateTreesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format=None):
        tree = get_object_or_404(CandidatesTrees, pk=pk)
        serializer = CandidateTreesSerializer(tree, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        tree = get_object_or_404(CandidatesTrees, pk=pk)
        tree.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
            average = CandidatesTrees.objects.exclude(numero_placa__isnull=True)
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
            ea.altura_comercial, 
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
            WHERE ef.nom_comunes = '%s'
            AND ea.numero_placa IS NOT NULL;
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
            WHERE ef.nom_comunes = '%s' AND ea.numero_placa IS NOT NULL;
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
        
class CandidatesSpecieUserView(APIView):
    def get(self, request, user_id, format=None):
        # Define la consulta SQL con un marcador de posición para el parámetro
        sql = """
            SELECT 
                ea.ShortcutIDEV,
                ea.user_id, 
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
            WHERE ea.user_id = %s AND ea.numero_placa IS NOT NULL;
        """

        # Ejecuta la consulta con el valor de user_id
        with connection.cursor() as cursor:
            cursor.execute(sql, [user_id])
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