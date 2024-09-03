from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count

from ..samples.models import Samples

class SamplesReport(APIView):
    def get(self, request, *args, **kwargs):
        # Usar ORM para realizar la consulta y agrupar por departamento y municipio
        results = (
            Samples.objects
            .select_related('evaluacion')  # Nos aseguramos de que la relación evaluacion sea seleccionada
            .values('evaluacion__departamento', 'evaluacion__municipio')  # Especificamos los campos de agrupamiento
            .annotate(total=Count('id'))  # Contamos el número de muestras por cada grupo
        )

        departamento_municipio_counts = {}
        departamento_total_counts = {}

        # Procesamos los resultados
        for result in results:
            departamento = result['evaluacion__departamento']
            municipio = result['evaluacion__municipio']
            total = result['total']

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





