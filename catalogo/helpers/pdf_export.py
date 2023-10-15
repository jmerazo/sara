from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Image, Flowable
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

class ImageWithText(Flowable):
    def __init__(self, image_path, text, width, height, style):
        Flowable.__init__(self)
        self.image_path = image_path
        self.text = text
        self.width = width
        self.height = height
        self.style = style

    def wrap(self, available_width, available_height):
        self.width = available_width
        self.height = available_height
        self.image_width = 50  # Ancho de la imagen
        self.total_width = self.image_width + 10  # Espacio entre la imagen y el texto

    def draw(self):
        self.canv.saveState()
        
        # Dibujar la imagen
        self.canv.drawImage(self.image_path, x=self._x, y=self._y, width=self.image_width, height=self.height)
        
        # Dibujar el texto
        self.canv.setFont(self.style.fontName, self.style.fontSize)
        self.canv.drawString(self._x + self.image_width + 10, self._y, self.text)
        
        self.canv.restoreState()

class ExportSpecies(APIView):
    def get(self, request, code, *args, **kwargs):
        specie = EspecieForestal.objects.filter(cod_especie=code).first()
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

        # Ruta de la imagen que deseas agregar al PDF
        image_path = 'ruta_de_la_imagen.jpg'

        image = Image(image_path, width=100, height=100)  # Puedes ajustar el ancho y el alto según tus necesidades
        elements.append(image)

        # Crear una lista de tuplas para los datos de la tabla
        table_data = []

        def add_table_row(label, value):
            if value is not None and value.strip() != "":
                label_paragraph = Paragraph(f"<b>{label}:</b>", title_style)
                value_paragraph = Paragraph(value, cell_style)
                table_data.append((label_paragraph, value_paragraph))

        # Agregar filas de datos a la tabla
        add_table_row("Nombre común", specieData.get('nom_comunes', ''))
        add_table_row("Otros nombres", specieData.get('otros_nombres', ''))
        add_table_row("Nombre científico", specieData.get('nombre_cientifico', ''))
        add_table_row("Sinonimos", specieData.get('sinonimos', ''))
        add_table_row("Familia", specieData.get('familia', ''))
        add_table_row("Distribución", specieData.get('distribucion', ''))
        add_table_row("Hojas", specieData.get('hojas', ''))
        add_table_row("Flor", specieData.get('flor', ''))
        add_table_row("Frutos", specieData.get('frutos', ''))
        add_table_row("Semillas", specieData.get('semillas', ''))
        add_table_row("Tallo", specieData.get('tallo', ''))
        add_table_row("Raíz", specieData.get('raiz', ''))

        # Crear la tabla con los datos
        especies_table = Table(table_data, colWidths=col_widths)
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
