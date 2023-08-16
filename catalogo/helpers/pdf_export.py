from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import utils
from io import BytesIO
from rest_framework.views import APIView
from datetime import datetime
from django.http import HttpResponse
from ..serializers import EspecieForestalSerializer
from ..models import EspecieForestal

# Crear un estilo personalizado para las celdas de la tabla
cell_style = getSampleStyleSheet()['Normal']
cell_style.alignment = 0  # Alinear a la izquierda
cell_style.wordWrap = 'CJK'  # Ajustar contenido para no desbordar
col_widths = [100, 400]  # Ancho de las columnas en puntos

# Crear un estilo personalizado para el título en negrita
title_style = ParagraphStyle(name='TitleStyle')
title_style.fontName = 'Helvetica-Bold'  # Cambia la fuente si es necesario
title_style.alignment = 0  # Alinear a la izquierda
title_style.leading = 14  # Espaciado entre líneas
title_style.textColor = 'black'  # Cambia el color del texto si es necesario
title_style.fontSize = 10  # Cambia el tamaño de la fuente si es necesario

class ExportSpecies(APIView):
    def get(self, request, code, *args, **kwargs):
        specie = EspecieForestal.objects.filter(cod_especie__icontains=code).first()
        specieData = EspecieForestalSerializer(specie).data

        current_date = datetime.now().strftime("%Y-%m-%d")

        file_name = f"{specieData['nom_comunes']}_{specieData['cod_especie']}_{current_date}.pdf"

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

        ltpsinonimos = Paragraph(specieData['sinonimos'])
        ltpdistribucion = Paragraph(specieData['distribucion'])
        ltphojas = Paragraph(specieData['hojas'])
        ltpflor = Paragraph(specieData['flor'])
        ltpfrutos = Paragraph(specieData['frutos'])
        ltpsemillas = Paragraph(specieData['semillas'])
        ltptallo = Paragraph(specieData['tallo'])
        ltpraiz = Paragraph(specieData['raiz'])

        especies_table = Table([
                                [Paragraph("<b>Nombre común:</b>", title_style), specieData['nom_comunes']],
                                [Paragraph("<b>Otros nombres:</b>", title_style), specieData['otros_nombres']],
                                [Paragraph("<b>Nombre científico:</b>", title_style), specieData['nombre_cientifico']],
                                [Paragraph("<b>Sinonimos:</b>", title_style), ltpsinonimos],
                                [Paragraph("<b>Familia:</b>", title_style), specieData['familia']],
                                [Paragraph("<b>Distribución:</b>", title_style), ltpdistribucion],
                                [Paragraph("<b>Hojas:</b>", title_style), ltphojas],
                                [Paragraph("<b>Flor:</b>", title_style), ltpflor],
                                [Paragraph("<b>Frutos:</b>", title_style), ltpfrutos],
                                [Paragraph("<b>Semillas:</b>", title_style), ltpsemillas],
                                [Paragraph("<b>Tallo:</b>", title_style), ltptallo],
                                [Paragraph("<b>Raíz:</b>", title_style), ltpraiz]
                                ], colWidths=col_widths)
        especies_table.setStyle([('STYLE', (0, 0), (-1, -1), cell_style)])
        elements.append(especies_table)

        # Construir el PDF
        doc.build(elements)

        # Obtener el contenido del BytesIO y devolverlo como respuesta
        pdf_content = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
