from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.http import Http404
from rest_framework.views import APIView
from django.db import connection
from .models import Monitorings
from ..candidates.models import CandidatesTrees
from .serializers import  MonitoringsSerializer
from rest_framework.permissions import IsAuthenticated
import random, string
from django.views.decorators.csrf import csrf_exempt

def generate_random_id(length):
            characters = string.ascii_letters + string.digits
            random_id = ''.join(random.choice(characters) for _ in range(length))
            return random_id

# VISTAS MONITOREOS
class SearchMonitoringCandidateView(APIView):
    def get(self, request, id, format=None):        
        search = Monitorings.objects.filter(ShortcutIDEV=id)
        serializer = MonitoringsSerializer(search, many=True)
        
        return Response(serializer.data)

class SearchMonitoringSpecieView(APIView):
    def get(self, request, code, format=None):
        # Obtener los valores de ShortcutIDEV desde la subconsulta
        shortcut_idevs = CandidatesTrees.objects.filter(cod_especie=code).values('ShortcutIDEV')
        
        # Realizar la búsqueda en la tabla Monitoring usando esos valores
        search = Monitorings.objects.filter(ShortcutIDEV__in=shortcut_idevs)
        
        serializer = MonitoringsSerializer(search, many=True)
        
        return Response(serializer.data)

class MonitoringsView(APIView):
    def get_queryset(self):
        queryset = Monitorings.objects.filter(
            evaluacion__numero_placa__isnull=False
        ).select_related(
            'evaluacion__cod_especie',  # Relación a la especie
            'user'  # Relación al usuario
        ).prefetch_related(
            'evaluacion'  # Pre-fetch de la relación de evaluación
        )

        return queryset

    def get(self, request, pk=None, format=None):
        queryset = self.get_queryset()

        if pk:
            queryset = queryset.filter(id=pk)

        serializer = MonitoringsSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = MonitoringsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format=None):
        monitoring = get_object_or_404(Monitorings, IDmonitoreo=pk)
        serializer = MonitoringsSerializer(monitoring, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        monitoring = get_object_or_404(Monitorings, IDmonitoreo=pk)
        monitoring.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MonitoringsUserView(APIView):
    def get_queryset(self, user):
        # Consulta SQL directa con parámetro
        query = """
            SELECT
                m.IDmonitoreo,
                m.user_id,
                ea.numero_placa, 
                ef.nom_comunes, 
                ef.nombre_cientifico, 
                ea.cod_especie_id, 
                m.fecha_monitoreo, 
                m.hora, 
                m.temperatura, 
                m.humedad, 
                m.precipitacion, 
                m.factor_climatico, 
                m.observaciones_temp, 
                m.fitosanitario, 
                m.afectacion, 
                m.observaciones_afec,
                m.follaje_porcentaje,
                m.observaciones_follaje,
                m.flor_abierta,
                m.flor_boton,
                m.color_flor,
                m.color_flor_otro,
                m.olor_flor,
                m.olor_flor_otro,
                m.fauna_flor,
                m.fauna_flor_otros,
                m.observaciones_flor,
                m.frutos_verdes,
                m.estado_madurez,
                m.color_fruto,
                m.color_fruto_otro,
                m.medida_peso_frutos,
                m.peso_frutos,
                m.fauna_frutos,
                m.fauna_frutos_otro,
                m.observacion_frutos,
                m.cant_semillas,
                m.medida_peso_sem,
                m.peso_semillas,
                m.observacion_semilla,
                m.observaciones
            FROM 
                monitoreo AS m 
            LEFT JOIN 
                evaluacion_as AS ea ON m.ShortcutIDEV = ea.ShortcutIDEV 
            LEFT JOIN 
                especie_forestal AS ef ON ef.cod_especie = ea.cod_especie_id
            WHERE ea.numero_placa IS NOT NULL AND m.user_id = %s;
        """
        # Ejecutar la consulta con el parámetro
        with connection.cursor() as cursor:
            cursor.execute(query, [user])
            result = cursor.fetchall()

        columns = [
            'IDmonitoreo', 'user_id', 'numero_placa', 'nom_comunes', 'nombre_cientifico',
            'cod_especie_id', 'fecha_monitoreo', 'hora', 'temperatura', 'humedad',
            'precipitacion', 'factor_climatico', 'observaciones_temp', 'fitosanitario',
            'afectacion', 'observaciones_afec', 'follaje_porcentaje',
            'observaciones_follaje', 'flor_abierta', 'flor_boton', 'color_flor',
            'color_flor_otro', 'olor_flor', 'olor_flor_otro', 'fauna_flor',
            'fauna_flor_otros', 'observaciones_flor', 'frutos_verdes', 'estado_madurez',
            'color_fruto', 'color_fruto_otro', 'medida_peso_frutos',
            'peso_frutos', 'fauna_frutos',
            'fauna_frutos_otro', 'observacion_frutos', 'cant_semillas',
            'medida_peso_sem', 'peso_semillas',
            'observacion_semilla', 'observaciones'
        ]
        queryset = [dict(zip(columns, row)) for row in result]

        return queryset

    def get(self, request, user_id, format=None):
        queryset = self.get_queryset(user_id)
        return Response(queryset)