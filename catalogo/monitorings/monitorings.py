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
        # Consulta SQL directa
        query = """
            SELECT
                m.IDmonitoreo,
                m.ShortcutIDEV_id,
                ea.numero_placa,
                m.fecha_monitoreo,
                m.hora,
                m.ubicacion_actual,
                m.validacion_ubicacion,
                m.user_id,
                u.first_name,
                u.last_name,
                ea.cod_especie_id,
                ef.habitos, 
                ef.nom_comunes, 
                ef.nombre_cientifico,                  
                m.temperatura, 
                m.humedad, 
                m.precipitacion, 
                m.factor_climatico, 
                m.observaciones_temp,
                m.observaciones_palma,
                m.cap,
                m.altura_total,
                m.altura_del_fuste, 
                m.eje_x,
                m.eje_y,
                m.eje_z,
                m.cantidad_anillos_tallo,
                m.fitosanitario,
                m.estado_fisico_palma, 
                m.afectacion, 
                m.observaciones_afec,
                m.cantidad_hojas_corona,
                m.estado_fisico_tallo,
                m.estado_sanitario_palma,
                m.factores_amenaza_individuos,
                m.follaje,
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
                m.estado_madurez_frutos_verdes,
                m.estado_madurez_frutos_maduros,
                m.estado_madurez_frutos_pintones,
                m.estado_madurez_frutos,
                m.estado_madurez,
                m.color_fruto,
                m.color_fruto_otro,
                m.fructificacion_copa,
                m.cantidad_frutos_rama,
                m.cant_ramas_fraccion_copa,
                m.porcentaje_fraccion_copa,
                m.cantidad_frutos_arbol,
                m.medida_peso_frutos,
                m.largo_fruto_maximo,
                m.ancho_fruto_maximo,
                m.largo_fruto_minimo,
                m.ancho_fruto_minimo,
                m.peso_frutos,
                m.cantidad_frutos_medidos,
                m.peso_por_fruto,
                m.peso_cascara,
                m.peso_pulpa_semillas,
                m.peso_pulpa,
                m.cant_semillas_arilo,
                m.peso_semillas_arilo,
                m.peso_una_semilla_arilo,
                m.fauna_frutos,
                m.fauna_frutos_otro,
                m.cant_racimos_capuchon,
                m.cant_racimos_flores,
                m.cant_racimos_frutos_verdes,
                m.cant_racimos_frutos_maduros,
                m.cant_racimos_senescente,
                m.peso_racimo_completo,
                m.peso_frutos_desgranados,
                m.cant_frutos_por_racimo,
                m.observacion_frutos,
                m.cant_semillas,
                m.medida_peso_sem,
                m.peso_semillas,
                m.cantidad_semillas_medidos,
                m.peso_por_semilla,
                m.cant_semillas_por_arbol,
                m.largo_semilla_maximo,
                m.ancho_semilla_maximo,
                m.largo_semilla_minimo,
                m.ancho_semila_minimo,
                m.observacion_semilla,
                m.cobertura,
                m.entorno,
                m.entorno_otro,
                m.observaciones
            FROM 
                monitoreo AS m 
            LEFT JOIN 
                evaluacion_as AS ea ON m.ShortcutIDEV_id = ea.ShortcutIDEV 
            LEFT JOIN 
                especie_forestal AS ef ON ef.cod_especie = ea.cod_especie_id
            LEFT JOIN
                Users AS u ON u.id = m.user_id
            WHERE ea.numero_placa IS NOT NULL;
        """
        # Ejecutar la consulta
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        columns = [
            'IDmonitoreo',
            'ShortcutIDEV',
            'numero_placa',
            'fecha_monitoreo',
            'hora',
            'ubicacion_actual',
            'validacion_ubicacion',
            'user_id',
            'first_name',
            'last_name',
            'cod_especie_id',
            'habitos',
            'nom_comunes',
            'nombre_cientifico',
            'temperatura',
            'humedad',
            'precipitacion',
            'factor_climatico',
            'observaciones_temp',
            'observaciones_palma',
            'cap',
            'altura_total',
            'altura_del_fuste',
            'eje_x',
            'eje_y',
            'eje_z',
            'cantidad_anillos_tallo',
            'fitosanitario',
            'estado_fisico_palma',
            'afectacion',
            'observaciones_afec',
            'cantidad_hojas_corona',
            'estado_fisico_tallo',
            'estado_sanitario_palma',
            'factores_amenaza_individuos',
            'follaje',
            'follaje_porcentaje',
            'observaciones_follaje',
            'flor_abierta',
            'flor_boton',
            'color_flor',
            'color_flor_otro',
            'olor_flor',
            'olor_flor_otro',
            'fauna_flor',
            'fauna_flor_otros',
            'observaciones_flor',
            'frutos_verdes',
            'estado_madurez_frutos_verdes',
            'estado_madurez_frutos_maduros',
            'estado_madurez_frutos_pintones',
            'estado_madurez_frutos',
            'estado_madurez',
            'color_fruto',
            'color_fruto_otro',
            'fructificacion_copa',
            'cantidad_frutos_rama',
            'cant_ramas_fraccion_copa',
            'porcentaje_fraccion_copa',
            'cantidad_frutos_arbol',
            'medida_peso_frutos',
            'largo_fruto_maximo',
            'ancho_fruto_maximo',
            'largo_fruto_minimo',
            'ancho_fruto_minimo',
            'peso_frutos',
            'cantidad_frutos_medidos',
            'peso_por_fruto',
            'peso_cascara',
            'peso_pulpa_semillas',
            'peso_pulpa',
            'cant_semillas_arilo',
            'peso_semillas_arilo',
            'peso_una_semilla_arilo',
            'fauna_frutos',
            'fauna_frutos_otro',
            'cant_racimos_capuchon',
            'cant_racimos_flores',
            'cant_racimos_frutos_verdes',
            'cant_racimos_frutos_maduros',
            'cant_racimos_senescente',
            'peso_racimo_completo',
            'peso_frutos_desgranados',
            'cant_frutos_por_racimo',
            'observacion_frutos',
            'cant_semillas',
            'medida_peso_sem',
            'peso_semillas',
            'cantidad_semillas_medidos',
            'peso_por_semilla',
            'cant_semillas_por_arbol',
            'largo_semilla_maximo',
            'ancho_semilla_maximo',
            'largo_semilla_minimo',
            'ancho_semila_minimo',
            'observacion_semilla',
            'cobertura',
            'entorno',
            'entorno_otro',
            'observaciones'
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
            return Monitorings.objects.get(pk=pk)
        except Monitorings.DoesNotExist:
            raise Http404

    def get(self, request, pk=None, format=None):
        monitorings = self.get_object(pk)

        if isinstance(monitorings, dict):
            # Convertir el resultado en una lista de diccionarios
            monitorings = [monitorings]

        return Response(monitorings)
    
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