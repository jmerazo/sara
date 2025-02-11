import os
import uuid
from PIL import Image
from django.http import Http404
from django.conf import settings
from django.db import transaction
from django.db import connection
from rest_framework import status
from django.db.models import Max, Q, F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import PageSerializer, PagesSerializer, SectionSerializer, SliderImagesSerializer
from .models import Page, Pages, Section, SliderImages
from ..species.serializers import SpecieForrestSerializer, SpecieForrestTopSerializer
from ..species.models import SpecieForrest


# VISTA PÁGINA ACERCA OTROS            
class PageView(APIView):
    def get_object(self, pk=None):
        if pk is not None:
            try:
                return Page.objects.get(pk=pk)
            except Page.DoesNotExist:
                raise Http404
        else:
            return Page.objects.all()

    def get(self, request, pk=None, format=None):
        pages = self.get_object(pk)
        
        if isinstance(pages, Page):
            serializer = PageSerializer(pages)
        else:
            serializer = PageSerializer(pages, many=True)
            
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        page = self.get_object(pk)
        serializer = PageSerializer(page, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        page = self.get_object(pk)
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UpdateCountVisitsView(APIView):
    def get(self, request, code, format=None):
        especie = SpecieForrest.objects.filter(code_specie=code).first()
        if especie is None:
            return Response({'error': 'Especie Forestal no encontrada'}, status=404)

        especie.views += 1
        especie.save()

        serializer = SpecieForrestSerializer(especie)
        return Response(serializer.data)
    
class TopSpeciesView(APIView):
    def get(self, request, pk=None, format=None):
        query = """
            SELECT sf.code_specie, sf.vernacularName, isr.img_general
            FROM especie_forestal_c AS sf
            LEFT JOIN img_species AS isr ON isr.specie_id = sf.id
            ORDER BY sf.views DESC
            LIMIT 4;
        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            queryset = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return Response(queryset)
            
class PagesView(APIView):
    def get_object(self, pk=None):
        if pk is not None:
            try:
                return Pages.objects.get(pk=pk)
            except Pages.DoesNotExist:
                raise Http404
        else:
            return Pages.objects.all()

    def get(self, request, pk=None, format=None):
        pages = self.get_object(pk)
        
        if isinstance(pages, Pages):
            serializer = PagesSerializer(pages)
        else:
            serializer = PagesSerializer(pages, many=True)
            
        return Response(serializer.data)
    
    @transaction.atomic
    def post(self, request, format=None):
        adjusted_data = request.data.copy()

        # Validación de que los campos requeridos existen
        required_fields = ['router', 'title']
        if not all(field in adjusted_data for field in required_fields):
            return Response({"error": "Faltan campos requeridos."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PagesSerializer(data=adjusted_data)
        if serializer.is_valid():
            serializer.save()  # Utiliza el método save del serializador si es posible

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Respuesta detallada de los errores de validación
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk, format=None):
        page = self.get_object(pk)
        serializer = PagesSerializer(page, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        page = self.get_object(pk)
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class SectionView(APIView):
    def get_object(self, pk=None):
        if pk is not None:
            try:
                return Section.objects.get(pk=pk)
            except Section.DoesNotExist:
                raise Http404
        else:
            return Section.objects.all()

    def get(self, request, pk=None, format=None):
        sections = self.get_object(pk)
        
        if isinstance(sections, Section):
            serializer = SectionSerializer(sections)
        else:
            serializer = SectionSerializer(sections, many=True)
            
        return Response(serializer.data)
    
    @transaction.atomic
    def post(self, request, format=None):
        adjusted_data = request.data.copy()

        # Validación de que los campos requeridos existen
        required_fields = ['page_id', 'section_title', 'content']
        if not all(field in adjusted_data for field in required_fields):
            return Response({"error": "Faltan campos requeridos."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SectionSerializer(data=adjusted_data)
        if serializer.is_valid():
            serializer.save()  # Utiliza el método save del serializador si es posible

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Respuesta detallada de los errores de validación
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        try:
            section = self.get_object(pk)
        except Http404:
            raise NotFound(detail="Sección no encontrada.", code=404)
        
        serializer = SectionSerializer(section, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        page = self.get_object(pk)
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SliderImagesView(APIView):
    def get_object(self, pk=None):
        if pk is not None:
            try:
                return SliderImages.objects.get(pk=pk)
            except SliderImages.DoesNotExist:
                raise Http404
        else:
            return SliderImages.objects.all()

    def get(self, request, pk=None, format=None):
        try:
            sliderImages = self.get_object(pk)
            if isinstance(sliderImages, Page):
                serializer = SliderImagesSerializer(sliderImages)
            else:
                serializer = SliderImagesSerializer(sliderImages, many=True)
            print('slider images ', sliderImages)

            return Response({
                'success': True,
                'msg': 'Imágenes obtenidas exitosamente.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'msg': 'Error al obtener las imágenes.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    parser_classes = (MultiPartParser, FormParser)    
    def post(self, request, format=None):
        try:
            # Verificar si se recibió un archivo en la solicitud
            if 'image' not in request.FILES:
                return Response({
                    'success': False,
                    'msg': 'No se encontró un archivo de imagen en la solicitud.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Verificar el número de imágenes existentes en el slider
            current_image_count = SliderImages.objects.count()
            if current_image_count >= 10:
                return Response({
                    'success': False,
                    'msg': 'No se pueden agregar más de 10 imágenes al slider.'
                }, status=status.HTTP_400_BAD_REQUEST)

            image = request.FILES['image']

            # Validar si el archivo subido es una imagen válida
            try:
                img = Image.open(image)
                img.verify()  # Verifica si el archivo es una imagen válida
            except Exception:
                return Response({
                    'success': False,
                    'msg': 'El archivo subido no es una imagen válida.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Crear la ruta del directorio para guardar las imágenes
            slider_directory = os.path.join(settings.BASE_DIR, 'images', 'slider')
            os.makedirs(slider_directory, exist_ok=True)

            # Generar un nombre único para la imagen
            unique_name = f"{uuid.uuid4()}{os.path.splitext(image.name)[1]}"
            file_path = os.path.join(slider_directory, unique_name)

            # Guardar el archivo en el directorio
            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

            # Generar la URL relativa para guardar en la base de datos
            relative_url = f"images/slider/{unique_name}"

            # Calcular el menor valor de `order` disponible
            all_orders = SliderImages.objects.values_list('order', flat=True)
            available_order = next((i for i in range(1, current_image_count + 2) if i not in all_orders), 1)

            # Agregar la URL al request.data para almacenarla en la base de datos
            data = request.data.copy()
            data['url'] = relative_url
            data['status'] = 1
            data['order'] = available_order

            # Validar y guardar los datos en la base de datos
            serializer = SliderImagesSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'msg': 'Imagen agregada exitosamente.',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)

            return Response({
                'success': False,
                'msg': 'Error al agregar la imagen.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'success': False,
                'msg': 'Error inesperado al agregar la imagen.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk, format=None):
        try:
            sliderImages = self.get_object(pk)  # Obtener el registro existente
            data = request.data.copy()  # Crear una copia de los datos enviados
            print('data ', data)

            status_value = request.data.get('status') or request.data.get('status[status]')
            print('status value ', status_value)
            if status_value is not None:
                try:
                    # Convertir el valor a entero y actualizar
                    sliderImages.status = int(status_value)
                    sliderImages.save()

                    return Response({
                        'success': True,
                        'msg': 'Estado actualizado exitosamente.',
                        'data': {'id': sliderImages.id, 'status': sliderImages.status}
                    }, status=status.HTTP_200_OK)
                except ValueError:
                    return Response({
                        'success': False,
                        'msg': 'El valor de "status" no es válido.',
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Verificar si hay una nueva imagen en los datos
            if 'image' in request.FILES:
                # Validar que el archivo subido es una imagen
                image = request.FILES['image']
                if not image.content_type.startswith("image/"):
                    return Response({
                        'success': False,
                        'msg': 'El archivo subido no es una imagen válida.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Eliminar la imagen existente si tiene una URL
                if sliderImages.url:
                    existing_image_path = os.path.join(settings.BASE_DIR, sliderImages.url)
                    if default_storage.exists(existing_image_path):
                        default_storage.delete(existing_image_path)

                # Procesar la nueva imagen
                slider_directory = os.path.join(settings.BASE_DIR, 'images', 'slider')
                os.makedirs(slider_directory, exist_ok=True)

                # Generar un nombre único para la nueva imagen
                unique_name = f"{uuid.uuid4()}{os.path.splitext(image.name)[1]}"
                file_path = os.path.join(slider_directory, unique_name)

                # Guardar la nueva imagen
                with default_storage.open(file_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)

                # Actualizar la URL en los datos
                data['url'] = f"images/slider/{unique_name}"

            # Serializar los datos actualizados
            serializer = SliderImagesSerializer(sliderImages, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'msg': 'Imagen o datos actualizados exitosamente.',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)

            return Response({
                'success': False,
                'msg': 'Error al actualizar la imagen o datos.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Http404:
            return Response({
                'success': False,
                'msg': 'Imagen no encontrada.',
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'success': False,
                'msg': 'Error inesperado al actualizar la imagen o datos.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk, format=None):
        try:
            # Obtener el objeto de la base de datos
            sliderImages = self.get_object(pk)

            # Obtener la ruta del archivo de la imagen
            image_path = os.path.join(settings.BASE_DIR, sliderImages.url)  # Asegúrate de que 'url' sea el campo correcto

            # Eliminar el archivo físico si existe
            if os.path.exists(image_path):
                os.remove(image_path)

            # Eliminar el registro de la base de datos
            sliderImages.delete()

            # Respuesta exitosa
            return Response({
                'success': True,
                'msg': 'Imagen eliminada exitosamente.'
            }, status=status.HTTP_200_OK)
        except Http404:
            # Respuesta si el objeto no existe
            return Response({
                'success': False,
                'msg': 'Imagen no encontrada.',
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Manejo de errores generales
            return Response({
                'success': False,
                'msg': 'Error inesperado al eliminar la imagen.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class OrderSliderImagesView(APIView):
    def patch(self, request, format=None):
        try:
            # Leer el array de imágenes con sus nuevos valores de `order`
            ordered_images = request.data.get('images', [])
            print('images ', ordered_images)
            if not ordered_images:
                return Response({
                    'success': False,
                    'msg': 'No se proporcionaron imágenes para actualizar.'
                }, status=status.HTTP_400_BAD_REQUEST)

            errors = []
            for image_data in ordered_images:
                try:
                    image = SliderImages.objects.get(id=image_data['id'])
                    image.order = image_data['order']
                    image.save()
                except SliderImages.DoesNotExist:
                    errors.append(f"Imagen con id {image_data['id']} no encontrada.")
                except Exception as e:
                    errors.append(f"Error al actualizar imagen con id {image_data['id']}: {str(e)}")

            if errors:
                return Response({
                    'success': False,
                    'msg': 'Algunos registros no pudieron ser actualizados.',
                    'errors': errors
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'success': True,
                'msg': 'Orden actualizado exitosamente.'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'msg': 'Error inesperado al actualizar el orden.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SliderView(APIView):
    def get_object(self, pk=None):
        if pk is not None:
            try:
                return SliderImages.objects.get(pk=pk)
            except SliderImages.DoesNotExist:
                raise Http404
        else:
            return SliderImages.objects.all()

    def get(self, request, pk=None, format=None):
        try:
            sliderImages = self.get_object(pk)
            if isinstance(sliderImages, Page):
                serializer = SliderImagesSerializer(sliderImages)
            else:
                serializer = SliderImagesSerializer(sliderImages, many=True)

            return Response({
                'success': True,
                'msg': 'Imágenes obtenidas exitosamente.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'msg': 'Error al obtener las imágenes.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)