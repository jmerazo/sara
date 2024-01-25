from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from django.db import connection
from .models import Monitoring
from .serializers import  MonitoringsSerializer
from rest_framework.permissions import IsAuthenticated
import random, string

def generate_random_id(length):
            characters = string.ascii_letters + string.digits
            random_id = ''.join(random.choice(characters) for _ in range(length))
            return random_id

# VISTAS MONITOREOS
class SearchMonitoringCandidateView(APIView):
    def get(self, request, id, format=None):        
        search = Monitoring.objects.filter(ShortcutIDEV=id)
        serializer = MonitoringsSerializer(search, many=True)
        
        return Response(serializer.data)

class SearchMonitoringSpecieView(APIView):
    def get(self, request, code, format=None):
        # Obtener los valores de ShortcutIDEV desde la subconsulta
        shortcut_idevs = CandidateTrees.objects.filter(cod_especie=code).values('ShortcutIDEV')
        
        # Realizar la búsqueda en la tabla Monitoring usando esos valores
        search = Monitoring.objects.filter(ShortcutIDEV__in=shortcut_idevs)
        
        serializer = MonitoringsSerializer(search, many=True)
        
        return Response(serializer.data)

class MonitoringsView(APIView):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        # Consulta SQL directa
        query = """
            SELECT
                m.IDmonitoreo,
                ea.numero_placa, 
                ef.nom_comunes, 
                ef.nombre_cientifico, 
                ea.cod_especie, 
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
                especie_forestal AS ef ON ef.cod_especie = ea.cod_especie;
        """
        # Ejecutar la consulta
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        columns = [
            'IDmonitoreo', 'numero_placa', 'nom_comunes', 'nombre_cientifico',
            'cod_especie', 'fecha_monitoreo', 'hora', 'temperatura', 'humedad',
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

    def get_object(self, pk=None):
        queryset = self.get_queryset()

        if pk is not None:
            try:
                monitoring = next(monitoring for monitoring in queryset if monitoring['IDmonitoreo'] == pk)
                return monitoring
            except StopIteration:
                raise Http404
        else:
            return queryset
        
    def get_object_for_delete(self, pk):
        # Este método se utiliza específicamente para la acción de eliminación.
        try:
            return Monitoring.objects.get(pk=pk)
        except Monitoring.DoesNotExist:
            raise Http404

    def get(self, request, pk=None, format=None):
        monitorings = self.get_object(pk)

        if isinstance(monitorings, dict):
            # Convertir el resultado en una lista de diccionarios
            monitorings = [monitorings]

        return Response(monitorings)