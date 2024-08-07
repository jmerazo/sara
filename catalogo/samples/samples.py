from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.http import Http404
from rest_framework.views import APIView
from django.db import connection
import random, string
from .models import Samples
from .serializers import SamplesSerializer, SamplesCreateSerializer
from rest_framework.permissions import IsAuthenticated

from .models import Samples
from ..candidates.models import CandidatesTrees
from ..species.models import SpecieForrest
from ..models import Users

def generate_random_id(length):
            characters = string.ascii_letters + string.digits
            random_id = ''.join(random.choice(characters) for _ in range(length))
            return random_id
        
# VISTA MUESTRAS
class SamplesView(APIView):
    def get_queryset(self):
        # Consulta SQL directa
        query = """
            SELECT
            m.id, 
            ea.numero_placa, 
            ef.vernacularName, 
            ef.nombre_cientifico, 
            ea.cod_especie_id, 
            m.fecha_coleccion, 
            m.nro_muestras, 
            CONCAT(u.first_name, ' ', u.last_name) AS colector_full_name,
            m.siglas_colector_ppal, 
            m.nro_coleccion, 
            m.voucher, 
            m.nombres_colectores, 
            m.codigo_muestra, 
            m.otros_nombres, 
            m.descripcion, 
            m.usos 
            FROM muestras_c AS m 
            LEFT JOIN evaluacion_as_c AS ea ON m.evaluacion_id = ea.id 
            LEFT JOIN especie_forestal_c AS ef ON ef.code_specie = ea.cod_especie_id
            INNER JOIN Users AS u ON m.user_id = u.id;
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
    
    def post(self, request, format=None):
        serializer = SamplesCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format=None):
        sample = get_object_or_404(Samples, idmuestra=pk)
        serializer = SamplesCreateSerializer(sample, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        sample = get_object_or_404(Samples, idmuestra=pk)
        sample.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)