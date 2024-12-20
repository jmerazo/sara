from datetime import date
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, F, Subquery, OuterRef, IntegerField
from .serializers import PropertySerializer, UserPropertyFileSerializer, UserPropertyFileAllSerializer, MonitoringPropertySerializer, PropertyCreateSerializer

from .models import Property, UserPropertyFile
from ..monitorings.models import Monitorings

class PropertyView(APIView):
    def get(self, request, pk=None, format=None):
        # Filtrar por 'pk' si se proporciona, de lo contrario obtener todos los registros
        if pk:
            queryset = Property.objects.filter(id=pk).select_related('p_user', 'p_departamento', 'p_municipio')
        else:
            queryset = Property.objects.all().select_related('p_user', 'p_departamento', 'p_municipio')

        # Serializar los datos
        serializer = PropertySerializer(queryset, many=True)

        # Retornar la respuesta en formato JSON
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = PropertyCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'msg': 'Propiedad creada exitosamente.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'msg': 'Error al crear la propiedad.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        nurseries = get_object_or_404(Property, pk=pk)
        serializer = PropertyCreateSerializer(nurseries, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'msg': 'Propiedad actualizada exitosamente.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'msg': 'Error al actualizar la propiedad.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        nurseries = get_object_or_404(Property, pk=pk)
        nurseries.delete()
        return Response({
            'success': True,
            'msg': 'Propiedad eliminada exitosamente.'
        }, status=status.HTTP_204_NO_CONTENT)
    
class PropertyUserIdView(APIView):
    def get(self, request, pk=None, format=None):
        if pk:
            queryset = Property.objects.filter(p_user_id=pk).select_related(
                'p_user', 'p_departamento', 'p_municipio'
            ).values(
                'id',
                'p_user__first_name',
                'p_user__last_name',
                'nombre_predio',
                'p_departamento__name',
                'p_municipio__name'
            )

        # Procesar los resultados para convertirlos en una lista de diccionarios
        predios = list(queryset)

        # Retornar la respuesta en formato JSON
        return Response(predios, status=status.HTTP_200_OK)
    
class UserPropertyFileView(APIView):
    def get(self, request, pk=None, format=None):
        if pk:
            queryset = UserPropertyFile.objects.filter(ep_usuario_id=pk)
        else:
            queryset = UserPropertyFile.objects.all()

        print(queryset)  # Esto te mostrará el queryset en la consola
        print(queryset.query)  # Esto imprimirá la consulta SQL generada

        serializer = UserPropertyFileAllSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = UserPropertyFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'msg': 'Especie asignada satisfactoriamente.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'msg': 'Error al asignar la especie.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        u_property = get_object_or_404(UserPropertyFile, pk=pk)
        serializer = UserPropertyFileSerializer(u_property, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'msg': 'Especie actualizada satisfactoriamente.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'msg': 'Error al actualizar la especie.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        u_property = get_object_or_404(UserPropertyFile, pk=pk)
        u_property.delete()
        return Response({
            'success': True,
            'msg': 'Especie eliminada satisfactoriamente.'
        }, status=status.HTTP_204_NO_CONTENT)
    
class MonitoringPropertyView(APIView):
    def get(self, request, format=None):
        # Definir la subconsulta para contar los monitoreos relacionados al usuario
        start_date = date(2024, 1, 1)

        subquery = Monitorings.objects.filter(
            user_id=OuterRef('ep_usuario_id'),
            evaluacion__cod_especie_id=OuterRef('ep_especie_id'),
            fecha_monitoreo__range=(start_date, date.today())
        ).values('user_id').annotate(
            cant_monitoreos_r=Count('id')
        ).values('cant_monitoreos_r')

        # Realizar la consulta principal con las anotaciones
        queryset = UserPropertyFile.objects.annotate(
            cant_monitoreos_r=Subquery(subquery, output_field=IntegerField()),
            diferencia_monitoreos=F('cant_monitoreos') - Subquery(subquery, output_field=IntegerField(), default=0)
        ).all()

        # Serializar los datos con el serializador actualizado
        serializer = MonitoringPropertySerializer(queryset, many=True)
        return Response(serializer.data)