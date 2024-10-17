from django.db import connection
from rest_framework import status
from django.db.models import Prefetch

from django.db.models import Q, Prefetch
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination

from .models import Monitorings
from ..candidates.models import CandidatesTrees
from ..species.models import SpecieForrest
from .serializers import  MonitoringsSerializer, MonitoringCreateSerializer

class MonitoringsPagination(PageNumberPagination):
    page_size = 50  # Tamaño de página predeterminado
    page_size_query_param = 'page_size'  # Permitir que el tamaño de página sea dinámico
    max_page_size = 1000  # Límite máximo de datos por página

    def get_paginated_response(self, data):
        return Response({
            'results': data,
            'total_items': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'current_page': self.page.number,  # Página actual
            'total_pages': self.page.paginator.num_pages,  # Total de páginas
        })

# VISTAS MONITOREOS
class SearchMonitoringCandidateView(APIView):
    def get(self, request, id, format=None):
        sql = """
            SELECT 
            ea.id,
            ea.numero_placa,
            ea.cod_expediente,
            ea.cod_especie_id,
            u.id,
            u.first_name,
            u.last_name,
            ef.id,
            ef.habit,
            ef.vernacularName,
            ef.nombre_cientifico,
            m.* 
            FROM monitoreo_c AS m
            INNER JOIN evaluacion_as_c as ea ON ea.id = m.evaluacion_id
            INNER JOIN Users as u ON u.id = m.user_id
            INNER JOIN especie_forestal_c AS ef ON ef.code_specie = ea.cod_especie_id
            WHERE evaluacion_id = %s;
        """
        
        with connection.cursor() as cursor:
            cursor.execute(sql, [id])
            result = cursor.fetchall()

            if not result:
                return Response({
                    'success': False,
                    'message': 'No se encontraron datos para este ID'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Obtén los nombres de las columnas y organiza los resultados
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in result]
        
            return Response({
                'success': True,
                'message': 'Consulta realizada con éxito',
                'data': data
            })

class SearchMonitoringSpecieView(APIView):
    def get(self, request, code, format=None):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    m.*
                FROM 
                    monitoreo_c AS m
                INNER JOIN 
                    evaluacion_as_c AS ea ON m.evaluacion_id = ea.id
                WHERE 
                    ea.cod_especie_id = %s;
            """, [code])
            
            columns = [col[0] for col in cursor.description]
            result = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        
        return Response(result)

class MonitoringsView(APIView):
    def get_queryset(self):
        queryset = Monitorings.objects.filter(
            evaluacion__numero_placa__isnull=False
        ).select_related(
            'evaluacion__cod_especie',
            'user'
        ).prefetch_related(
            Prefetch('evaluacion', queryset=CandidatesTrees.objects.all()),
            Prefetch('evaluacion__cod_especie', queryset=SpecieForrest.objects.all())
        ).order_by('-fecha_monitoreo')

        # Obtener el término de búsqueda desde los parámetros de consulta
        search_term = self.request.query_params.get('search', None)
        if search_term:
            # Aplicar filtros de búsqueda en múltiples campos
            queryset = queryset.filter(
                Q(evaluacion__numero_placa__icontains=search_term) |
                Q(evaluacion__cod_especie__vernacularName__icontains=search_term) |  # nombre vulgar
                Q(evaluacion__cod_especie__scientificName__icontains=search_term) |  # nombre científico
                Q(evaluacion__cod_especie__scientificNameAuthorship__icontains=search_term) |  # autoría del nombre científico
                Q(evaluacion__cod_especie__nombre_cientifico__icontains=search_term)  # nombre científico alternativo
            )

        return queryset

    def get(self, request, pk=None, format=None):
        queryset = self.get_queryset()
        paginator = MonitoringsPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = MonitoringsSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = MonitoringsSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = MonitoringCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Monitoreo creado con éxito!',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Error al crear el monitoreo',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format=None):
        monitoring = get_object_or_404(Monitorings, id=pk)
        serializer = MonitoringCreateSerializer(monitoring, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Monitoreo actualizado con éxito!',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'message': 'Error al actualizar el monitoreo',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        monitoring = get_object_or_404(Monitorings, id=pk)
        monitoring.delete()
        return Response({
            'success': True,
            'message': 'Monitoreo eliminado con éxito!'
        }, status=status.HTTP_204_NO_CONTENT)

class MonitoringsUserView(APIView):
    def get_queryset(self, user):
        queryset = Monitorings.objects.filter(
            evaluacion__numero_placa__isnull=False,
            user_id=user
        ).select_related(
            'user', 'evaluacion__cod_especie'
        )
        return queryset

    def get(self, request, user_id, format=None):
        queryset = self.get_queryset(user_id)
        serializer = MonitoringsSerializer(queryset, many=True)
        return Response(serializer.data)
    
class DownloadMonitoringsView(APIView):
    def get_queryset(self):
        sql_query = """
            SELECT u.id, ea.numero_placa, u.first_name, u.last_name, ef.vernacularName, 
                   ef.scientificName, ef.scientificNameAuthorship, ef.code_specie, m.*
            FROM monitoreo_c AS m
            INNER JOIN Users AS u ON u.id = m.user_id
            INNER JOIN evaluacion_as_c AS ea ON ea.id = m.evaluacion_id
            INNER JOIN especie_forestal_c AS ef ON ef.code_specie = ea.cod_especie_id
            WHERE ea.numero_placa IS NOT NULL
            ORDER BY m.fecha_monitoreo;
        """
        
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()

        # Convierte los resultados a una lista de diccionarios para facilitar el retorno en JSON
        data = [dict(zip(columns, row)) for row in results]
        return data

    def get(self, request, format=None):
        # Obtiene la lista de diccionarios con la data de la consulta SQL
        data = self.get_queryset()
        
        # Devuelve los datos como JSON
        return Response(data)