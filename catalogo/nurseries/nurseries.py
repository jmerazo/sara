from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection
from .serializers import NurseriesSerializer, UserNurseriesSerializer, UsersNurseriesSerializer
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
            INNER JOIN departments AS d ON d.id = v.department_id
            INNER JOIN cities AS c ON c.id = v.city_id;
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

            # Verificar si el vivero ya existe en el diccionario, de lo contrario, agregarlo
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

            # Agregar la especie forestal a la lista de especies del vivero
            especie = {
                'especie_forestal_id': row_dict['especie_forestal_id'],
                'nom_comunes': row_dict['nom_comunes'],
                'nombre_cientifico_especie': row_dict['nombre_cientifico_especie'],
                'nombre_autor_especie': row_dict['nombre_autor_especie'],
                'tipo_venta': row_dict['tipo_venta'],
                'unidad_medida': row_dict['unidad_medida'],
                'cantidad_stock': row_dict['cantidad_stock'],
                'ventas_realizadas': row_dict['ventas_realizadas'],
                'observaciones': row_dict['observaciones'],
                'fecha_registro': row_dict['fecha_registro'],
                'fecha_actualizacion': row_dict['fecha_actualizacion']
            }

            viveros[vivero_id]['especies'].append(especie)

        # Retornar los datos en formato de respuesta
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
    
class NurseriesAdminView(APIView):
    def get(self, request, format=None):
        query = """
            SELECT v.id, v.nombre_vivero, v.nit, v.representante_legal_id, u.first_name, u.last_name, 
                   v.ubicacion, v.email, v.telefono, v.department_id, d.name AS departamento, 
                   v.city_id, c.name AS municipio, v.direccion, v.logo, v.active
            FROM viveros AS v
            INNER JOIN Users AS u ON u.id = v.representante_legal_id
            INNER JOIN departments AS d ON d.id = v.department_id
            INNER JOIN cities AS c ON c.id = v.city_id;
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        # Procesar los resultados en una lista de diccionarios
        viveros = []
        for row in results:
            row_dict = {columns[index]: value for index, value in enumerate(row)}
            viveros.append({
                'id': row_dict['id'],
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
                'direccion': row_dict['direccion'],
                'logo': row_dict['logo'],
                'activo': row_dict['active']
            })

        return Response(viveros)
    
    def post(self, request, format=None):
        serializer = UsersNurseriesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format=None):
        unurseries = get_object_or_404(UserNurseries, pk=pk)
        serializer = UsersNurseriesSerializer(unurseries, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        unurseries = get_object_or_404(Nurseries, pk=pk)
        unurseries.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)