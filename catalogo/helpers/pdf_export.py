from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import Paragraph, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
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

def dibujar_encabezado(c, img_path):
    # Verificar si la imagen existe
    if not os.path.exists(img_path):
        print("Archivo de imagen no encontrado:", img_path)
        return
    ancho_original_px = 200  # Ancho original en píxeles
    alto_original_px = 159   # Alto original en píxeles
    dpi = 500  # Resolución deseada

    ancho_inch = ancho_original_px / dpi  # Ancho en pulgadas
    alto_inch = alto_original_px / dpi    # Alto en pulgadas

    # Añadir imagen al encabezado en la posición y tamaño correctos
    c.drawImage(img_path, inch, 8 * inch, ancho_inch * inch, alto_inch * inch, preserveAspectRatio=True, mask='auto')
    # Añadir texto del encabezado
    c.setFont('Montserrat', 8)
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    c.drawString(3 * inch, 8.2 * inch, f'Sistema de información de Semillas y Árboles de la Región sur de la Amazonía - {fecha_actual}')

def dibujar_pie_pagina(c, width):
    c.setFont('Montserrat', 8)
    anio_actual = datetime.now().year
    texto1 = f"© Sara - {anio_actual}"
    texto2 = "Corporación para el Desarrollo Sostenible del Sur de la Amazonia"
    texto3 = "Cra. 17 14-85 Mocoa - Putumayo"

    # Calcular el ancho del texto y la posición x para centrar
    ancho_texto1 = c.stringWidth(texto1, 'Helvetica', 8)
    ancho_texto2 = c.stringWidth(texto2, 'Helvetica', 8)
    ancho_texto3 = c.stringWidth(texto3, 'Helvetica', 8)

    x1 = (width - ancho_texto1) / 2
    x2 = (width - ancho_texto2) / 2
    x3 = (width - ancho_texto3) / 2

    # Dibujar el texto centrado
    c.drawString(x1, 0.5 * inch, texto1)
    c.drawString(x2, 0.35 * inch, texto2)
    c.drawString(x3, 0.2 * inch, texto3)

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

                    # Crear el canvas
                    c = canvas.Canvas(buffer, pagesize=landscape(letter))
                    width, height = landscape(letter)

                    # Obtener la ruta absoluta a la imagen
                    ruta_directorio_actual = os.path.dirname(__file__)
                    ruta_imagen = os.path.join(ruta_directorio_actual, 'resources', 'imgs', 'sara.png')
                    # Dibujar el encabezado
                    dibujar_encabezado(c, ruta_imagen)

                    # Definir márgenes
                    margin = inch
                    # Definir el ancho de las columnas
                    column_width = (width - 3 * margin) / 2 
                    y_position = height - 3 * inch

                    # Definir el tamaño del título y el espacio (padding) después del título
                    padding_after_title = 20  # Este es el espacio después del título, ajústalo según sea necesario                    

                    title_text = [f'<font name="Montserrat-BoldItalic"><i>{specieData["nombre_cientifico_especie"]}</i></font>' f'<font name="Montserrat-Bold">{specieData["nombre_autor_especie"]}</font>']
                    # Crear el estilo para el título
                    title_style = ParagraphStyle(
                        name='TitleStyle',
                        fontSize=18,
                        leading=22,  # Espacio entre líneas
                        textColor=colors.black,
                        alignment=1  # Centrado
                    )

                    title_paragraph = Paragraph(" ".join(title_text), title_style)

                    # Dibujar el título usando Paragraph en lugar de canvas.drawString
                    w, h = title_paragraph.wrap(width, height)
                    title_paragraph.drawOn(c, (width - w) / 2, height - margin - h)

                    # Ajustar la posición inicial para el resto del contenido
                    y_position = height - margin - h - padding_after_title

                    # Crear un estilo para el contenido de texto
                    content_style = ParagraphStyle(
                        name='ContentStyle',
                        fontName='Montserrat',
                        fontSize=10,
                        textColor=colors.black,
                        leading=10  # Espacio entre líneas
                    )
                    
                    # Crear párrafos para el texto en la columna derecha
                    data_specie = [
                        f'<font name="Montserrat-Bold"><b>Nombre común:</b></font> <font name="Montserrat">{specieData["nom_comunes"]}</font>',
                        f'<font name="Montserrat-Bold"><b>Otros nombres:</b></font> <font name="Montserrat">{specieData["otros_nombres"]}</font>',
                        f'<font name="Montserrat-Bold"><b>Nombre científico:</b></font> {" ".join(title_text)}',
                        f'<font name="Montserrat-Bold"><b>Sinónimos:</b></font> <font name="Montserrat">{specieData["sinonimos"]}</font>',
                        f'<font name="Montserrat-Bold"><b>Familia:</b></font> <font name="Montserrat">{specieData["familia"]}</font>',
                        f'<font name="Montserrat-Bold"><b>Distribución:</b></font> <font name="Montserrat">{specieData["distribucion"]}</font>',
                        f'<font name="Montserrat-Bold"><b>Hábito:</b></font> <font name="Montserrat">{specieData["habito"]}</font>',
                    ]

                    #y_position = height - margin  # Ajustar la posición inicial
                    for text in data_specie:
                        p = Paragraph(text, style=content_style)
                        w, h = p.wrap(column_width, height)
                        p.drawOn(c, margin, y_position - h)
                        y_position -= h + 12  # Espaciado entre párrafos
                    
                    # Restablecer y_position para las imágenes
                    y_position = height - margin - h - padding_after_title

                    # Función para ajustar y dibujar una imagen
                    def ajustar_y_dibujar_imagen(image_path, espacio_ancho, espacio_alto, x_pos, y_pos):
                        img = Image(image_path)
                        ancho_original, alto_original = img.imageWidth, img.imageHeight
                        factor_escala_ancho = espacio_ancho / ancho_original
                        factor_escala_alto = espacio_alto / alto_original
                        factor_escala = min(factor_escala_ancho, factor_escala_alto)
                        img.drawWidth = ancho_original * factor_escala
                        img.drawHeight = alto_original * factor_escala
                        img.drawOn(c, x_pos, y_pos - img.drawHeight)
                        return img.drawHeight

                    # Calcular el espacio disponible para las imágenes
                    espacio_disponible_ancho = column_width
                    ajuste_alineacion = 15  
                    espacio_disponible_alto = y_position - margin - ajuste_alineacion # Dividir el espacio verticalmente entre las dos imágenes

                    # Posición x para las imágenes (centradas en la columna derecha)
                    posicion_x_imagen = width / 2 + (column_width - espacio_disponible_ancho) / 2

                    # Ajustar y dibujar la primera imagen
                    altura_img1 = ajustar_y_dibujar_imagen(specieData['img_general'], espacio_disponible_ancho, 
                                                            espacio_disponible_alto, posicion_x_imagen, y_position - ajuste_alineacion)

                    # Actualizar la posición y para la segunda imagen
                    posicion_y_imagen2 = y_position - altura_img1 - ajuste_alineacion - margin

                    # Ajustar y dibujar la segunda imagen
                    ajustar_y_dibujar_imagen(specieData['img_landscape_one'], espacio_disponible_ancho, 
                                            espacio_disponible_alto, posicion_x_imagen, posicion_y_imagen2)
                    
                    # Antes de finalizar la página, dibujar el pie de página
                    dibujar_pie_pagina(c, width)
                    # Finalizar el canvas
                    c.showPage()

                    # ============ B R E A K == PAGE == 1 ===============

                    dibujar_encabezado(c, ruta_imagen)

                    data_specie_page2 = [
                        f'<font name="Montserrat-Bold"><b>Hojas:</b></font> <font name="Montserrat">{specieData["hojas"]}</font>',
                        f'<font name="Montserrat-Bold"><b>Flores:</b></font> <font name="Montserrat">{specieData["flor"]}</font>',
                        f'<font name="Montserrat-Bold"><b>Frutos:</b></font> <font name="Montserrat">{specieData["frutos"]}</font>',
                        f'<font name="Montserrat-Bold"><b>Semillas:</b></font> <font name="Montserrat">{specieData["semillas"]}</font>',
                        f'<font name="Montserrat-Bold"><b>Tallo:</b></font> <font name="Montserrat">{specieData["tallo"]}</font>',
                        f'<font name="Montserrat-Bold"><b>Raíz:</b></font> <font name="Montserrat">{specieData["raiz"]}</font>',
                    ]

                    # Ajustar la posición inicial para el texto en la columna derecha
                    y_position_texto = height - margin - h
                    x_position_texto = width / 2 + margin * -1  # Aumentar el espacio para el texto
                    column_width_texto = width / 2 - margin * 0.2  # Ajustar el ancho de la columna de texto

                    for text in data_specie_page2:
                        p = Paragraph(text, style=content_style)
                        w, h = p.wrap(column_width_texto, height)
                        if y_position_texto - h < margin:  # Si no hay espacio, crea una nueva página
                            c.showPage()
                            dibujar_encabezado(c, ruta_imagen)
                            y_position_texto = height - margin
                        p.drawOn(c, x_position_texto, y_position_texto - h)
                        y_position_texto -= h + 12  # Espaciado entre párrafos

                    # Restablecer y_position para las imágenes
                    y_position_imagenes = height - margin - h - padding_after_title

                    # Calcular el espacio disponible para las imágenes
                    espacio_disponible_ancho = column_width  # Ajustar según el espacio real disponible
                    ajuste_alineacion = 15  

                    # Posición x para las imágenes (Ajustar para alinear a la izquierda)
                    posicion_x_imagen = margin

                    # Lista de imágenes para dibujar
                    imagenes = [specieData['img_leafs'], specieData['img_flowers'], specieData['img_fruits'], specieData['img_seeds'], specieData['img_stem']]

                    # Calcular el espacio vertical total disponible para las imágenes
                    espacio_vertical_total = height - 2 * margin - h

                    # Número total de imágenes
                    num_imagenes = len(imagenes)

                    # Espacio vertical disponible por imagen
                    espacio_por_imagen = espacio_vertical_total / num_imagenes

                    # Ajustar y dibujar las imágenes
                    y_position = height - margin - h - padding_after_title

                    # Ajustar y dibujar las imágenes
                    for img_path in imagenes:
                        altura_img = ajustar_y_dibujar_imagen(img_path, espacio_disponible_ancho, 
                                                            espacio_por_imagen, posicion_x_imagen, y_position_imagenes)

                        y_position_imagenes -= altura_img
                        if y_position_imagenes < margin:
                            # Si no hay suficiente espacio
                            break

                    dibujar_pie_pagina(c, width)
                    c.showPage()        
                    c.save()

                    # Crear el PDF
                    #doc.build(elements)
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