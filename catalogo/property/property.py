from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection
from .serializers import PropertySerializer, UserPropertyFileSerializer
from rest_framework.permissions import IsAuthenticated

from .models import Property, UserPropertyFile

class PropertyView(APIView):
    def get(self, request, pk=None, format=None):
        if pk:
            query = """
                SELECT p.id, u.first_name, u.last_name, p.nombre_predio, d.name AS departamento_name, c.name AS ciudad_name
                FROM predios AS p
                INNER JOIN Users AS u ON u.id = p.p_user_id
                INNER JOIN departments AS d ON d.id = p.p_departamento_id
                INNER JOIN cities AS c ON c.id = p.p_municipio_id
                WHERE p.id = %s;
            """
            params = [pk]
        else:
            query = """
                SELECT p.id, u.first_name, u.last_name, p.nombre_predio, d.name AS departamento_name, c.name AS ciudad_name
                FROM predios AS p
                INNER JOIN Users AS u ON u.id = p.p_user_id
                INNER JOIN departments AS d ON d.id = p.p_departamento_id
                INNER JOIN cities AS c ON c.id = p.p_municipio_id;
            """
            params = []

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        # Procesar los resultados para convertirlos en una lista de diccionarios
        predios = []
        for row in results:
            predio = dict(zip(columns, row))
            predios.append(predio)

        # Retornar la respuesta en formato JSON
        return Response(predios, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = PropertySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format=None):
        nurseries = get_object_or_404(Property, pk=pk)
        serializer = PropertySerializer(nurseries, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        nurseries = get_object_or_404(Property, pk=pk)
        nurseries.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class UserPropertyFileView(APIView):
    def get(self, request, pk=None, format=None):
        if pk:
            query = """
                SELECT uep.id, uep.ep_especie_cod, ef.nom_comunes, ef.nombre_cientifico_especie, ef.nombre_autor_especie, uep.ep_usuario_id, u.first_name, u.last_name, uep.cantidad_individuos, uep.cant_productiva, uep.cant_remanente, uep.ep_predio_id, p.nombre_predio, uep.expediente
                FROM usuario_expediente_predio AS uep
                INNER JOIN especie_forestal AS ef ON ef.cod_especie = uep.ep_especie_cod
                INNER JOIN Users AS u ON u.id = uep.ep_usuario_id
                INNER JOIN predios AS p ON p.id = uep.ep_predio_id
                WHERE uep.id = %s;
            """
            params = [pk]
        else:
            query = """
                SELECT uep.id, uep.ep_especie_cod, ef.nom_comunes, ef.nombre_cientifico_especie, ef.nombre_autor_especie, uep.ep_usuario_id, u.first_name, u.last_name, uep.cantidad_individuos, uep.cant_productiva, uep.cant_remanente, uep.ep_predio_id, p.nombre_predio, uep.expediente
                FROM usuario_expediente_predio AS uep
                INNER JOIN especie_forestal AS ef ON ef.cod_especie = uep.ep_especie_cod
                INNER JOIN Users AS u ON u.id = uep.ep_usuario_id
                INNER JOIN predios AS p ON p.id = uep.ep_predio_id;
            """
            params = []

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        # Procesar los resultados para convertirlos en una lista de diccionarios
        user_predios = []
        for row in results:
            upredio = dict(zip(columns, row))
            user_predios.append(upredio)

        # Retornar la respuesta en formato JSON
        return Response(user_predios, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = UserPropertyFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format=None):
        u_property = get_object_or_404(UserPropertyFile, pk=pk)
        serializer = UserPropertyFileSerializer(u_property, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        u_property = get_object_or_404(UserPropertyFile, pk=pk)
        u_property.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)