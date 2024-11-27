from pdf2image import convert_from_path
import os

def pdf_to_images(pdf_path, output_folder):
    """
    Convierte un archivo PDF en imágenes y las guarda en el directorio de salida.
    
    Si las imágenes ya existen en el directorio de salida, se omite la conversión.
    
    :param pdf_path: Ruta del archivo PDF.
    :param output_folder: Ruta del directorio donde se guardarán las imágenes.
    :return: Lista de rutas de las imágenes generadas.
    """
    # Crear el directorio de salida si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Verificar si las imágenes ya existen
    existing_images = sorted(
        [os.path.join(output_folder, img) for img in os.listdir(output_folder) if img.endswith('.jpg')]
    )
    if existing_images:
        print(f"Imágenes ya existen en {output_folder}, omitiendo conversión.")
        return existing_images
    
    # Convertir PDF a imágenes
    try:
        images = convert_from_path(pdf_path)
        image_paths = []
        for i, image in enumerate(images):
            output_path = os.path.join(output_folder, f"page_{i + 1}.jpg")
            image.save(output_path, "JPEG")
            image_paths.append(output_path)
        return image_paths
    except Exception as e:
        print(f"Error al convertir el PDF a imágenes: {e}")
        return []
