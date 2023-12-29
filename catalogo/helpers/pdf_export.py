from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, PageTemplate, Paragraph, Spacer, Image, Frame, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from rest_framework.views import APIView
from datetime import datetime
from django.http import HttpResponse
from django.db.models import F
from django.db import connection
import os

# Registro de fuentes
font_path = os.path.join(os.path.dirname(__file__), 'resources', 'Montserrat', 'Montserrat-Regular.ttf')
pdfmetrics.registerFont(TTFont('Montserrat', font_path))

font_path_bold = os.path.join(os.path.dirname(__file__), 'resources', 'Montserrat', 'Montserrat-Bold.ttf')
pdfmetrics.registerFont(TTFont('Montserrat-Bold', font_path_bold))

font_path_italic = os.path.join(os.path.dirname(__file__), 'resources', 'Montserrat', 'Montserrat-Italic.ttf')
pdfmetrics.registerFont(TTFont('Montserrat-Italic', font_path_italic))

font_path_bolditalic = os.path.join(os.path.dirname(__file__), 'resources', 'Montserrat', 'Montserrat-BoldItalic.ttf')
pdfmetrics.registerFont(TTFont('Montserrat-BoldItalic', font_path_bolditalic))

class ExportSpecies(APIView):
    def get(self, request, code, *args, **kwargs):
        #Consulta SQL información
        query = f"""
            SELECT ef.cod_especie, ef.nom_comunes, ef.otros_nombres, ie.img_general, ef.nombre_cientifico_especie, ef.nombre_autor_especie, ef.sinonimos, ef.familia, ef.distribucion, ef.habito, ef.hojas, ie.img_leafs, ef.flor, ie.img_flowers, ef.frutos, ie.img_fruits, ef.semillas, ie.img_seeds, ef.tallo, ie.img_stem, ef.raiz, ie.img_landscape_one
            FROM especie_forestal AS ef
            LEFT JOIN img_species AS ie 
            ON ef.ShortcutID = ie.specie_id
            WHERE ef.cod_especie = '{code}';
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            try:
                rows = cursor.fetchall()
                if rows:
                    specieData = dict(zip([col[0] for col in cursor.description], rows[0]))
                    current_date = datetime.now().strftime("%Y-%m-%d") # Fecha del documento

                    file_name = f"{specieData['nom_comunes']}_{specieData['cod_especie']}_{current_date}.pdf" #Nombre del arhivo PDF
                    buffer = BytesIO() 
                    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter)) # Crear archivo pdf
                    elements = [] 
                    # Definir una plantilla de página
                    page_template = PageTemplate(frames=[
                        Frame(inch, inch, 6.5 * inch, 9 * inch, id='normal'),  # Marco principal
                        Frame(inch, inch, 6.5 * inch, 0.5 * inch, id='footer', showBoundary=1),  # Marco para el pie de página
                    ]) 

                    doc.addPageTemplates([page_template])  

                    # Crear el estilo para el título
                    title_style = ParagraphStyle(
                        name='TitleStyle',
                        fontSize=18,
                        textColor=colors.black,
                        alignment=1,
                        spaceAfter=12,
                    )

                    # Crear el título con nombres concatenados y formatos diferentes
                    title_text = [
                        f'<font name="Montserrat-BoldItalic"><i>{specieData["nombre_cientifico_especie"]}</i></font> '
                        f'<font name="Montserrat-Bold">{specieData["nombre_autor_especie"]}</font>',
                    ]

                    title = Paragraph(" ".join(title_text), title_style)

                    # Agregar el título al contenido
                    elements.append(title)
                    elements.append(Spacer(1, 12))

                    # Crear un estilo para el contenido de texto
                    content_style = ParagraphStyle(
                        name='ContentStyle',
                        fontSize=12,
                        textColor=colors.black,
                        leading=14  # Espacio entre líneas
                    )

                    # Crear un marco para la primera columna
                    frame1 = Frame(30, 50, 500, 700, showBoundary=True)  # (x, y, ancho, alto)
                    elements.append(frame1)

                    # Crear párrafos para el texto en la columna derecha
                    nombre_comun_paragraph = Paragraph(f'<font name="Montserrat-Bold"><b>Nombre común:</b></font> <font name="Montserrat">{specieData["nom_comunes"]}</font>', content_style)
                    otros_nombres_paragraph = Paragraph(f'<font name="Montserrat-Bold"><b>Otros nombres:</b></font> <font name="Montserrat">{specieData["otros_nombres"]}</font>', content_style)
                    nombre_cientifico_paragraph = Paragraph(f'<font name="Montserrat-Bold"><b>Nombre científico:</b></font> {" ".join(title_text)}', content_style)
                    sinonimos_paragraph = Paragraph(f'<font name="Montserrat-Bold"><b>Sinónimos:</b></font> <font name="Montserrat">{specieData["sinonimos"]}</font>', content_style)
                    familia_paragraph = Paragraph(f'<font name="Montserrat-Bold"><b>Familia:</b></font> <font name="Montserrat">{specieData["familia"]}</font>', content_style)
                    distribucion_paragraph = Paragraph(f'<font name="Montserrat-Bold"><b>Distribución:</b></font> <font name="Montserrat">{specieData["distribucion"]}</font>', content_style)
                    habito_paragraph = Paragraph(f'<font name="Montserrat-Bold"><b>Hábito:</b></font> <font name="Montserrat">{specieData["habito"]}</font>', content_style)
                    
                    imageGeneral = Image(specieData['img_general'], width=451, height=225)
                    frame1.addFromList(imageGeneral, doc)

                    frame2 = Frame(300, 50, 250, 700, showBoundary=True)  # (x, y, ancho, alto)
                    elements.append(frame2)
                    frame2.addFromList(nombre_comun_paragraph, doc)

                    text_elements = [
                        nombre_comun_paragraph,
                        otros_nombres_paragraph,
                        nombre_cientifico_paragraph,
                        sinonimos_paragraph,
                        familia_paragraph,
                        distribucion_paragraph,
                        habito_paragraph,
                    ]

                    """ elements.append(imageGeneral)
                    elements.append(nombre_comun_paragraph)
                    elements.append(otros_nombres_paragraph)
                    elements.append(nombre_cientifico_paragraph)
                    elements.append(sinonimos_paragraph)
                    elements.append(familia_paragraph)
                    elements.append(distribucion_paragraph)
                    elements.append(habito_paragraph) """

                    # Crear el PDF
                    doc.build(elements)
                    pdf_content = buffer.getvalue()
                    buffer.close()

                    # Create an HTTP response with the PDF
                    response = HttpResponse(content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                    response.write(pdf_content)
                    return response

                else:
                    return HttpResponse("No data found for this species code", status=404)

            except Exception as e:
                print(str(e))  # Maneja cualquier excepción que pueda ocurrir durante la ejecución de la consulta SQL
                return HttpResponse