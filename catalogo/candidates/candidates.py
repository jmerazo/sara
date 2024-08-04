from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from decimal import Decimal
import random, string

from ..species.models import SpecieForrest
from .models import CandidatesTrees
from .serializers import CandidateTreesSerializer

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
        # Realiza la consulta sin select_related ni prefetch_related
        queryset = CandidatesTrees.objects.filter(
            numero_placa__isnull=False,
            abcisa_xy__isnull=False
        )

        specie_dict = {specie.code_specie: specie for specie in SpecieForrest.objects.all()}

        geo_format = []
        for ea in queryset:
            ef = specie_dict.get(ea.cod_especie_id)

            if ef is None:
                continue

            if ea.abcisa_xy:
                latitud, longitud = map(float, ea.abcisa_xy.split(', '))
            else:
                latitud, longitud = None, None

            geo_fixed = {
                'codigo': ef.code_specie,
                'numero_placa': ea.numero_placa,
                'departamento': ea.departamento,
                'municipio': ea.municipio,
                'vereda': ea.locality,
                'nombre_del_predio': ea.nombre_del_predio,
                'lat': latitud,
                'lon': longitud,
                'coordenadas': ea.abcisa_xy,
                'resultado': ea.resultado,
                'nombre_comun': ef.scientificName,
                'nombre_cientifico': ef.nombre_cientifico,
                'taxon_key': ef.taxon_key,
                'habito': ef.habit
            }
            geo_format.append(geo_fixed)
            
        return Response(geo_format)
    
class CandidatesTreesView(APIView):
    def get(self, request, np=None, format=None): 
        if np:
            # Obtener un objeto específico por pk
            queryset = CandidatesTrees.objects.filter(ShortcutIDEV=np)
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
    
    def put(self, request, np, format=None):
        tree = get_object_or_404(CandidatesTrees, numero_placa=np)
        serializer = CandidateTreesSerializer(tree, data=request.data)
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
    def get(self, request, nom, format=None):
        # Realiza la consulta utilizando el ORM de Django
        queryset = CandidatesTrees.objects.filter(
            numero_placa__isnull=False,
            cod_especie__nom_comunes=nom
        ).select_related('cod_especie').values(
            'ShortcutIDEV', 'numero_placa', 'cod_expediente', 'cod_especie', 
            'fecha_evaluacion', 'departamento', 'municipio', 'altitud', 
            'altura_total', 'altura_fuste', 'cobertura', 'cober_otro', 
            'entorno_individuo', 'entorno_otro', 'especies_forestales_asociadas', 
            'dominancia_if', 'forma_fuste', 'dominancia', 'alt_bifurcacion', 
            'estado_copa', 'posicion_copa', 'fitosanitario', 'presencia', 
            'resultado', 'evaluacion', 'observaciones'
        )

        # Filtra las filas que contienen valores NULL y sustituye 'None' por None
        filtered_queryset = []
        for row in queryset:
            row_dict = {}
            for col, value in row.items():
                if value == 'None':
                    value = None
                row_dict[col] = value
            filtered_queryset.append(row_dict)

        return Response(filtered_queryset)
        
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