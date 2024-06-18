from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import connection
from rest_framework.permissions import IsAuthenticated

class SamplesReport(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            sql_query = """
                SELECT e.departamento, e.municipio, COUNT(*) AS total FROM muestras m 
                INNER JOIN evaluacion_as e ON m.nro_placa = e.ShortcutIDEV 
                GROUP BY e.departamento, e.municipio
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





