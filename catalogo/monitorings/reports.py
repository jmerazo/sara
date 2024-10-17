from rest_framework.response import Response
from rest_framework.views import APIView
from django_pandas.io import read_frame
from django.db.models import F
from django.db.models import Count, OuterRef, Subquery
from datetime import datetime
from collections import defaultdict
from calendar import monthrange
from django.db import connection

from .models import Monitorings
from ..candidates.models import CandidatesTrees
from ..species.models import SpecieForrest
from .serializers import  MonitoringsSerializer

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from django_pandas.io import read_frame

# Endpoint 
# - monitores realizados mes, pendientes, totales, por municipio, por departamento

class MonitoringReport(APIView):
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
    def get(self, request, *args, **kwargs):
        queryset = Monitorings.objects.filter(evaluacion__numero_placa__isnull=False) \
            .values('evaluacion__departamento', 'evaluacion__municipio') \
            .annotate(total=Count('id'))

        departamento_totals = {}
        municipio_totals = {}

        for item in queryset:
            departamento = item['evaluacion__departamento']
            municipio = item['evaluacion__municipio']
            total = item['total']
            
            if departamento not in departamento_totals:
                departamento_totals[departamento] = 0
            if municipio not in municipio_totals:
                municipio_totals[municipio] = 0

            departamento_totals[departamento] += total
            municipio_totals[municipio] += total

        response_data = {
            'departamentos': departamento_totals,
            'municipios': municipio_totals
        }

        return Response(response_data)    

class TrainMonitoring(APIView):
    def get(self, request, *args, **kwargs):
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
            INNER JOIN 
                especie_forestal AS ef ON ef.cod_especie = ea.cod_especie
            WHERE ea.numero_placa IS NOT NULL;
        """
            
        
        # Codifica la consulta SQL en bytes
        query = query.encode('utf-8')
        
        # Ejecuta la consulta SQL
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            data = cursor.fetchall()
        
        # Convierte los resultados en un DataFrame de pandas
        df = pd.DataFrame(data, columns=columns)

        # Continúa con el preprocesamiento de tus datos aquí
        df['cod_especie'] = df['cod_especie'].astype('category').cat.codes
        df.fillna(df.mean(), inplace=True)

        # Definir tus características y objetivo
        # Asegúrate de definir 'otras_columnas_no_relevantes' correctamente
        X = df.drop(columns=['IDmonitoreo', 'observaciones_temp', 'observaciones_afec', 'observaciones_follaje', 'olor_flor_otro', 'fauna_flor_otros', 'observaciones_flor', 'color_fruto_otro', 'observacion_frutos', 'observacion_semilla', 'entorno_otro', 'observaciones'])
        y = df['cod_especie']

        # Dividir en conjunto de entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Construir y entrenar el modelo
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Evaluar el modelo
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        print('accuracy: ', accuracy)

        # Asegúrate de devolver un objeto Response
        return Response({'message': 'Model trained', 'accuracy': accuracy})
    
class reportFruitAndFlower(APIView):
    def get(self, request, format=None): 
        query = """
        SELECT m.IDmonitoreo, m.ShortcutIDEV_id, m.fecha_monitoreo, ea.cod_especie_id, ef.nom_comunes, ef.nombre_cientifico_especie, ef.nombre_autor_especie, m.flor_abierta, m.frutos_verdes
        FROM monitoreo AS m
        INNER JOIN evaluacion_as AS ea ON ea.ShortcutIDEV = m.ShortcutIDEV_id
        INNER JOIN especie_forestal AS ef ON ef.cod_especie = ea.cod_especie_id
        WHERE m.flor_abierta IS NOT NULL AND m.frutos_verdes IS NOT NULL;
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        # Crear una lista de diccionarios, cada uno representando una fila del resultado
        queryset = [{columns[index]: value for index, value in enumerate(row)} for row in results]

        return Response(queryset)