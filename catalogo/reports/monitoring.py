from rest_framework import viewsets
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status, generics, permissions
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from django.db.models import Count, OuterRef, Subquery
from datetime import datetime
from collections import defaultdict
from calendar import monthrange
from django.db import connection

from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from ..models import CandidateTrees, Monitoring
# Endpoint 
# - monitores realizados mes, pendientes, totales, por municipio, por departamento

class MonitoringReport(APIView):
    def get(self, request, *args, **kwargs):
        now = datetime.now().date()
        first_day = now.replace(day=1)
        end_day = now.replace(day=monthrange(now.year, now.month)[1])

        # Subconsulta para obtener los ShortcutIDEV de monitoreos realizados en el mes actual
        monitoreos_realizados = Monitoring.objects.filter(
            fecha_monitoreo__gte=first_day,
            fecha_monitoreo__lte=end_day
        ).values('ShortcutIDEV')

        # Consulta para contar los monitoreos pendientes y realizados
        tree_counts = CandidateTrees.objects.annotate(
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
    def get(self, request, *args, **kwargs):
        now = datetime.now().date()
        first_day = now.replace(day=1)
        end_day = now.replace(day=monthrange(now.year, now.month)[1])

        monitoreos_realizados = Monitoring.objects.filter(
            fecha_monitoreo__gte=first_day,
            fecha_monitoreo__lte=end_day
        ).values('ShortcutIDEV')

        total_monitoreos = CandidateTrees.objects.annotate(
            realizado=Subquery(
                monitoreos_realizados.filter(ShortcutIDEV=OuterRef('ShortcutIDEV'))
                .values('ShortcutIDEV')
                .annotate(count=Count('ShortcutIDEV'))
                .values('count')
            )
        ).filter(numero_placa__isnull=False).values('departamento', 'realizado', 'municipio')

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
            
            if realizado and realizado > 0:
                department_totals[departamento]['monitoreos_realizados_mes'] += 1
                department_totals[departamento]['municipios'][municipio]['monitoreos_realizados_mes'] += 1
            else:
                department_totals[departamento]['monitoreos_pendientes_mes'] += 1
                department_totals[departamento]['municipios'][municipio]['monitoreos_pendientes_mes'] += 1

            department_totals[departamento]['total_monitoreos_mes'] += 1
            department_totals[departamento]['municipios'][municipio]['total_monitoreos_mes'] += 1
        
        response_data = {
            'locates_totals': department_totals
        }

        return Response(response_data)

class MonitoringReportTotal(APIView):
    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            sql_query = """
                SELECT ea.departamento, ea.municipio, COUNT(*) AS total
                FROM monitoreo AS m
                INNER JOIN evaluacion_as AS ea ON m.ShortcutIDEV = ea.ShortcutIDEV
                GROUP BY ea.departamento, ea.municipio
            """
            cursor.execute(sql_query)
            results = cursor.fetchall()

        departamento_municipio_counts = {}
        departamento_total_counts = {}

        for departamento, municipio, total in results:
            if departamento not in departamento_municipio_counts:
                departamento_municipio_counts[departamento] = {}
                departamento_total_counts[departamento] = 0

            departamento_municipio_counts[departamento][municipio] = total
            departamento_total_counts[departamento] += total

        response_data = {}

        for departamento, total in departamento_total_counts.items():
            departamento_data = {
                "total": total,
                "municipios": departamento_municipio_counts[departamento]
            }
            response_data[departamento] = departamento_data

        return Response(response_data)