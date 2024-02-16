from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, OuterRef, Subquery
from datetime import datetime
from collections import defaultdict
from calendar import monthrange
from django.db import connection
from rest_framework.permissions import IsAuthenticated
from ..candidates.models import CandidatesTrees
from .models import Monitorings
# Endpoint 
# - monitores realizados mes, pendientes, totales, por municipio, por departamento

class MonitoringReport(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        now = datetime.now().date()
        first_day = now.replace(day=1)
        end_day = now.replace(day=monthrange(now.year, now.month)[1])

        # Subconsulta para obtener los ShortcutIDEV de monitoreos realizados en el mes actual
        monitoreos_realizados = Monitorings.objects.filter(
            fecha_monitoreo__gte=first_day,
            fecha_monitoreo__lte=end_day
        ).values('ShortcutIDEV')

        # Consulta para contar los monitoreos pendientes y realizados
        tree_counts = CandidatesTrees.objects.annotate(
            realizado=Subquery(
                monitoreos_realizados.filter(ShortcutIDEV=OuterRef('ShortcutIDEV'))
                .values('ShortcutIDEV')
                .annotate(count=Count('ShortcutIDEV'))
                .values('count')
            )
        ).filter(numero_placa__isnull=False).values('realizado').annotate(count=Count('ShortcutIDEV'))

        total_monitoring = sum(tree['count'] for tree in tree_counts)
        made_monitoring = sum(tree['count'] for tree in tree_counts if tree['realizado'] and tree['realizado'] > 0)
        earring_monitoring = total_monitoring - made_monitoring

        response_data = {
            'made_monitoring': made_monitoring,
            'earring_monitoring': earring_monitoring,
            'total_monitoring': total_monitoring
        }

        return Response(response_data)
    
class MonitoringReportLocates(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        now = datetime.now().date()
        first_day = now.replace(day=1)
        end_day = now.replace(day=monthrange(now.year, now.month)[1])

        monitoreos_realizados = Monitorings.objects.filter(
            fecha_monitoreo__gte=first_day,
            fecha_monitoreo__lte=end_day
        ).values('ShortcutIDEV')

        total_monitoreos = CandidatesTrees.objects.annotate(
            realizado=Subquery(
                monitoreos_realizados.filter(ShortcutIDEV=OuterRef('ShortcutIDEV'))
                .values('ShortcutIDEV')
                .annotate(count=Count('ShortcutIDEV'))
                .values('count')
            )
        ).filter(numero_placa__isnull=False).values('departamento', 'realizado', 'municipio')

        municipios_por_departamento = {
            "Putumayo": ["Sibundoy", "Santiago", "San Francisco", "Colon", "Mocoa", "Villagarzón", "Puerto Guzmán", "Puerto Caicedo", "Puerto Asís", "Orito", "Valle del Guamuez", "San Miguel", "Puerto Leguízamo"],
            "Caquetá": ["Albania", "Belpen de los Andaquíes", "Cartagena del Chairá", "Curillo", "El Doncello", "El Paujil", "Florencia", "La Montañita", "Morelia", "Puerto Milán", "Puerto Rico", "San José del Fragua", "San Vicente del Caguán", "Solano", "Solita", "Valparaíso"],
            "Amazonas": ["Leticia", "Puerto Nariño", "El Encanto", "La Pedrera", "La Chorrera", "Tarapacá", "Puerto Santander", "Mirití Paraná", "Puerto Alegría", "Puerto Arica", "La Victoria"]
        }

        department_totals = defaultdict(lambda: {
            'monitoreos_realizados_mes': 0,
            'monitoreos_pendientes_mes': 0,
            'total_monitoreos_mes': 0,
            'municipios': defaultdict(lambda: {
                'monitoreos_realizados_mes': 0,
                'monitoreos_pendientes_mes': 0,
                'total_monitoreos_mes': 0
            })
        })

        for entry in total_monitoreos:
            departamento = entry['departamento']
            municipio = entry['municipio']
            realizado = entry['realizado']
            
            # Verificar si el municipio pertenece al departamento actual
            if municipio in municipios_por_departamento.get(departamento, []):
                if realizado and realizado > 0:
                    department_totals[departamento]['monitoreos_realizados_mes'] += 1
                    department_totals[departamento]['municipios'][municipio]['monitoreos_realizados_mes'] += 1
                else:
                    department_totals[departamento]['monitoreos_pendientes_mes'] += 1
                    department_totals[departamento]['municipios'][municipio]['monitoreos_pendientes_mes'] += 1

                department_totals[departamento]['total_monitoreos_mes'] += 1
                department_totals[departamento]['municipios'][municipio]['total_monitoreos_mes'] += 1
        
        response_data = {
            'departamentos': dict(department_totals)
        }

        return Response(response_data)

class MonitoringReportTotal(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            sql_query = """
                SELECT ea.departamento, ea.municipio, COUNT(*) AS total
                FROM monitoreo AS m
                INNER JOIN evaluacion_as AS ea ON m.ShortcutIDEV = ea.ShortcutIDEV
                WHERE ea.numero_placa IS NOT NULL
                GROUP BY ea.departamento, ea.municipio
            """
            cursor.execute(sql_query)
            results = cursor.fetchall()

        departamento_totals = {}
        municipio_totals = {}

        for departamento, municipio, total in results:
            if departamento not in departamento_totals:
                departamento_totals[departamento] = 0
            if municipio not in municipio_totals:
                municipio_totals[municipio] = 0

            departamento_totals[departamento] += total
            municipio_totals[municipio] += total

        response_data = {
            'departamentos': dict(departamento_totals),
            'municipios': dict(municipio_totals)
        }

        return Response(response_data)