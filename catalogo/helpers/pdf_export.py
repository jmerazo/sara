from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from io import BytesIO
from rest_framework.views import APIView
from django.http import FileResponse
from datetime import datetime
from django.http import HttpResponse
import os
from ..serializers import EspecieForestalSerializer
from ..models import EspecieForestal

class ExportSpecies(APIView):
    def get(self, request, *args, **kwargs):
        specie = EspecieForestal.objects.all()
        specieData = EspecieForestalSerializer(specie, many=True).data

        current_date = datetime.now().strftime("%Y-%m-%d")

        file_name = f"{specieData[0]['nom_comunes']}_{specieData[0]['cod_especie']}_{current_date}.pdf"

        # Crear un objeto BytesIO para almacenar el PDF en memoria
        buffer = BytesIO()

        # Lógica para generar el archivo PDF
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Agregar contenido al PDF
        elements = []

        # Agregar un encabezado
        header_text = "Reporte de Especies Forestales"
        header = Paragraph(header_text)
        elements.append(header)

        # Agregar una tabla con datos de especies
        especies_table = Table([[specieData[0]['nom_comunes'], specieData[0]['cod_especie']]])
        elements.append(especies_table)

        # Construir el PDF
        doc.build(elements)

        # Obtener el contenido del BytesIO y devolverlo como respuesta
        pdf_content = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
