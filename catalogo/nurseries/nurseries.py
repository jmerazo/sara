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
        SELECT uv.id, uv.vivero_id, uv.especie_forestal_id, ef.nom_comunes, ef.nombre_cientifico_especie, ef.nombre_autor_especie, uv.tipo_venta, uv.unidad_medida, uv.cantidad_stock, uv.ventas_realizadas, uv.observaciones, uv.fecha_registro, uv.fecha_actualizacion, uv.activo, v.nombre_vivero, v.nit, v.representante_legal_id, u.first_name, u.last_name, v.ubicacion, v.email, v.telefono, d.name AS departamento, c.name AS municipio
        FROM UserEspecieForestal AS uv
        INNER JOIN viveros AS v ON v.id = uv.vivero_id
        INNER JOIN especie_forestal AS ef ON ef.cod_especie = uv.especie_forestal_id
        INNER JOIN Users AS u ON u.id = v.representante_legal_id
        INNER JOIN departments AS d ON d.id = v.department
        INNER JOIN cities AS c ON c.id = v.city;
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        # Procesar los resultados para agrupar las especies por vivero
        viveros = {}
        for row in results:
            row_dict = {columns[index]: value for index, value in enumerate(row)}
            vivero_id = row_dict['vivero_id']

            if vivero_id not in viveros:
                viveros[vivero_id] = {
                    'id': row_dict['id'],
                    'vivero_id': row_dict['vivero_id'],
                    'nombre_vivero': row_dict['nombre_vivero'],
                    'nit': row_dict['nit'],
                    'representante_legal_id': row_dict['representante_legal_id'],
                    'first_name': row_dict['first_name'],
                    'last_name': row_dict['last_name'],
                    'ubicacion': row_dict['ubicacion'],
                    'email': row_dict['email'],
                    'telefono': row_dict['telefono'],
                    'departamento': row_dict['departamento'],
                    'municipio': row_dict['municipio'],
                    'activo': row_dict['activo'],
                    'especies': []
                }
            
            especie = {
                'especie_forestal_id': row_dict['especie_forestal_id'],
                'nom_comunes': row_dict['nom_comunes'],
                'nombre_cientifico_especie': row_dict['nombre_cientifico_especie'],
                'nombre_autor_especie': row_dict['nombre_autor_especie'],
                'tipo_venta': row_dict['tipo_venta'],
                'unidad_medida': row_dict['unidad_medida'],
                'cantidad_stock': row_dict['cantidad_stock'],
                'ventas_realizadas': row_dict['ventas_realizadas'],
                'observaciones': row_dict['observaciones']
            }

            viveros[vivero_id]['especies'].append(especie)

        return Response(list(viveros.values()))

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