from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection
from .serializers import NurseriesSerializer, UserNurseriesSerializer, UsersNurseriesSerializer

from .models import Nurseries, UserNurseries

class NurseriesView(APIView):
    def get(self, request, format=None):
        # Obtener todos los viveros
        nurseries = Nurseries.objects.select_related(
            'representante_legal', 
            'department', 
            'city'
        ).all()

        # Usar ORM para obtener los datos de UserNurseries
        user_nurseries = UserNurseries.objects.select_related(
            'vivero__representante_legal', 
            'vivero__department', 
            'vivero__city',
            'especie_forestal'
        ).all()

        # Serializar los datos de UserNurseries
        serializer = UserNurseriesSerializer(user_nurseries, many=True)
        data = serializer.data

        # Agrupar por vivero y preparar la respuesta final
        viveros = {}
        for nursery in nurseries:
            viveros[nursery.id] = {
                'id': nursery.id,
                'nombre_vivero': nursery.nombre_vivero,
                'nit': nursery.nit,
                'representante_legal_id': nursery.representante_legal.id,
                'first_name': nursery.representante_legal.first_name,
                'last_name': nursery.representante_legal.last_name,
                'ubicacion': nursery.ubicacion,
                'email': nursery.email,
                'telefono': nursery.telefono,
                'departamento': nursery.department.name,
                'municipio': nursery.city.name,
                'activo': nursery.active,  # Asumimos que todos los viveros están activos por defecto
                'clase_vivero': nursery.clase_vivero,
                'vigencia_registro': nursery.vigencia_registro,
                'tipo_registro': nursery.tipo_registro,
                'numero_registro_ica': nursery.numero_registro_ica,
                'especies': []
            }

        for item in data:
            vivero_id = item['vivero']['id']
            
            # Agregar la especie forestal a la lista de especies del vivero
            especie = {
                'especie_forestal_id': item['especie_forestal']['code_specie'],
                'nom_comunes': item['especie_forestal']['vernacularName'],
                'nombre_cientifico_especie': item['especie_forestal']['scientificName'],
                'nombre_autor_especie': item['especie_forestal']['scientificNameAuthorship'],
                'tipo_venta': item['tipo_venta'],
                'unidad_medida': item['unidad_medida'],
                'cantidad_stock': item['cantidad_stock'],
                'ventas_realizadas': item['ventas_realizadas'],
                'observaciones': item['observaciones']
            }

            viveros[vivero_id]['especies'].append(especie)
            viveros[vivero_id]['activo'] = item['activo']

        # Retornar la respuesta en formato JSON
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
        # Utiliza `select_related` para optimizar la consulta con relaciones ForeignKey
        queryset = Nurseries.objects.select_related(
            'representante_legal', 'department', 'city'
        ).all()

        # Usa el serializer que has definido para serializar los resultados
        serializer = NurseriesSerializer(queryset, many=True)
        
        # Retorna los datos serializados en formato JSON
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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