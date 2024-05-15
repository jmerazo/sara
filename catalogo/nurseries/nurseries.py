from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection
from .serializers import NurseriesSerializer, UserNurseriesSerializer
from rest_framework.permissions import IsAuthenticated

from .models import Nurseries, UserNurseries

class NurseriesView(APIView):
    def get(self, request, format=None): 
        query = """
        SELECT uv.id, uv.vivero_id, uv.especie_forestal_id, ef.nom_comunes, ef.nombre_cientifico_especie, ef.nombre_autor_especie, uv.tipo_venta, uv.unidad_medida, uv.cantidad_stock, uv.ventas_realizadas, uv.observaciones, uv.fecha_registro, uv.fecha_actualizacion, uv.activo, v.nombre_vivero, v.nit, v.representante_legal_id, u.first_name, u.last_name, v.ubicacion, v.email, v.telefono
        FROM UserEspecieForestal AS uv
        INNER JOIN viveros AS v ON v.id = uv.vivero_id
        INNER JOIN especie_forestal AS ef ON ef.cod_especie = uv.especie_forestal_id
        INNER JOIN Users AS u ON u.id = v.representante_legal_id;
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        # Crear una lista de diccionarios, cada uno representando una fila del resultado
        queryset = [{columns[index]: value for index, value in enumerate(row)} for row in results]

        return Response(queryset)

    def post(self, request, format=None):
        serializer = NurseriesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format=None):
        nurseries = get_object_or_404(Nurseries, pk=pk)
        serializer = NurseriesSerializer(nurseries, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        nurseries = get_object_or_404(Nurseries, pk=pk)
        nurseries.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)