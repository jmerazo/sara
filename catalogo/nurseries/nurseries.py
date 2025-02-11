import os
import uuid
from django.db import connection
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from .serializers import NurseriesSerializer, UserNurseriesSerializer, UsersNurseriesSerializer, NurseriesCreateSerializer, UserNurseriesCreateSerializer

from .models import Nurseries, UserNurseries

class NurseriesView(APIView):
    def get(self, request, format=None):
        # Obtener todos los viveros
        nurseries = Nurseries.objects.select_related(
            'representante_legal', 
            'department', 
            'city'
        ).all()

        # Usar ORM para obtener los datos de UserNurseries
        user_nurseries = UserNurseries.objects.select_related(
            'vivero__representante_legal', 
            'vivero__department', 
            'vivero__city',
            'especie_forestal'
        ).all()

        # Serializar los datos de UserNurseries
        serializer = UserNurseriesSerializer(user_nurseries, many=True)
        data = serializer.data

        # Agrupar por vivero y preparar la respuesta final
        viveros = {}
        for nursery in nurseries:
            viveros[nursery.id] = {
                'id': nursery.id,
                'nombre_vivero': nursery.nombre_vivero,
                'nit': nursery.nit,
                'representante_legal_id': nursery.representante_legal.id,
                'first_name': nursery.representante_legal.first_name,
                'last_name': nursery.representante_legal.last_name,
                'ubicacion': nursery.ubicacion,
                'email': nursery.email,
                'telefono': nursery.telefono,
                'departamento': nursery.department.name,
                'municipio': nursery.city.name,
                'activo': nursery.active,  # Asumimos que todos los viveros están activos por defecto
                'logo': nursery.logo,
                'clase_vivero': nursery.clase_vivero,
                'vigencia_registro': nursery.vigencia_registro,
                'tipo_registro': nursery.tipo_registro,
                'numero_registro_ica': nursery.numero_registro_ica,
                'especies': []
            }

        for item in data:
            vivero_id = item['vivero']['id']
            
            # Agregar la especie forestal a la lista de especies del vivero
            especie = {
                'especie_forestal_id': item['especie_forestal']['code_specie'],
                'nom_comunes': item['especie_forestal']['vernacularName'],
                'nombre_cientifico_especie': item['especie_forestal']['scientificName'],
                'nombre_autor_especie': item['especie_forestal']['scientificNameAuthorship'],
                'tipo_venta': item['tipo_venta'],
                'unidad_medida': item['unidad_medida'],
                'cantidad_stock': item['cantidad_stock'],
                'ventas_realizadas': item['ventas_realizadas'],
                'observaciones': item['observaciones']
            }

            viveros[vivero_id]['especies'].append(especie)
            viveros[vivero_id]['activo'] = item['activo']

        # Retornar la respuesta en formato JSON
        return Response(list(viveros.values()))

    def post(self, request, format=None):
        nit = request.data.get('nit')  # Obtén el nit desde los datos enviados en la solicitud
        image = request.FILES.get('logo')  # Asumiendo que el archivo se envía en un campo llamado "logo"

        if not nit:
            return Response({"error": "NIT is required"}, status=status.HTTP_400_BAD_REQUEST)

        if image:
            # Generar nombre aleatorio para la imagen
            random_filename = f"{uuid.uuid4().hex}.png"  # Genera un nombre aleatorio con extensión .jpeg

            # Crear la ruta donde se almacenará la imagen: /images/img/nit/<NIT>/nombre_aleatorio.jpeg
            nit_folder = os.path.join(settings.MEDIA_ROOT, 'img', str(nit))
            if not os.path.exists(nit_folder):
                os.makedirs(nit_folder)  # Crear la carpeta si no existe

            # Ruta completa de la imagen
            image_path = os.path.join(nit_folder, random_filename)

            # Guardar la imagen
            with default_storage.open(image_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

            # Ruta relativa para almacenar en la base de datos
            relative_image_path = os.path.join('img', str(nit), random_filename)

            # Modificar los datos antes de guardar en la base de datos
            request.data['logo'] = relative_image_path

        serializer = NurseriesCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Vivero asignado correctamente!',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Error al asignar el vivero!',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format=None):
        nurseries = get_object_or_404(Nurseries, pk=pk)
        serializer = NurseriesSerializer(nurseries, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        nurseries = get_object_or_404(Nurseries, pk=pk)
        nurseries.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class NurseriesAdminView(APIView):
    def get(self, request, format=None):
        # Utiliza `select_related` para optimizar la consulta con relaciones ForeignKey
        queryset = Nurseries.objects.select_related(
            'representante_legal', 'department', 'city'
        ).all()

        # Usa el serializer que has definido para serializar los resultados
        serializer = NurseriesSerializer(queryset, many=True)
        
        # Retorna los datos serializados en formato JSON
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        serializer = UsersNurseriesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format=None):
        unurseries = get_object_or_404(UserNurseries, pk=pk)
        serializer = UsersNurseriesSerializer(unurseries, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        unurseries = get_object_or_404(UserNurseries, pk=pk)
        unurseries.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class NurseriesUserView(APIView):
    def get(self, request, rlid=None, format=None):
        if rlid is None:
            return Response({"error": "El parámetro 'representante_legal_id' es obligatorio."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Realiza la consulta usando SQL crudo
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT v.id, v.nombre_vivero, v.nit, v.`representante_legal_id`, ef.`code_specie`, ef.`vernacularName`, ef.`scientificName`, ef.`scientificNameAuthorship`, uef.*
                FROM UserEspecieForestal AS uef
                INNER JOIN viveros AS v ON uef.vivero_id = v.id
                INNER JOIN especie_forestal_c AS ef ON ef.`code_specie` = uef.`especie_forestal_id`
                WHERE v.representante_legal_id = %s
            """, [rlid])

            # Obtén los nombres de las columnas
            columns = [col[0] for col in cursor.description]
            # Convierte los resultados en una lista de diccionarios
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Retorna los datos como JSON
        return Response(rows, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        serializer = UserNurseriesCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Especie agregada al inventario!',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'message': 'Error al actualizar al agregar la especie al inventario!',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, rlid, format=None):
        unurseries = get_object_or_404(UserNurseries, pk=rlid)
        print('Request data:', request.data)
        serializer = UserNurseriesCreateSerializer(unurseries, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Inventario actualizado!',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'message': 'Error al actualizar el inventario!',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, rlid, format=None):
        try:
            # Intentar obtener el registro con la clave primaria proporcionada
            unurseries = get_object_or_404(UserNurseries, pk=rlid)
            unurseries.delete()
            return Response({
                'success': True,
                'message': 'Especie eliminada del inventario',
            }, status=status.HTTP_200_OK)
        except Exception as e:
            # Manejo de cualquier excepción durante la eliminación
            return Response({
                'success': False,
                'message': 'Error al eliminar la especie del inventario!',
                'error': str(e)  # Devuelve el mensaje de error para diagnóstico
            }, status=status.HTTP_400_BAD_REQUEST)
    
class NurseryUserStateView(APIView):       
    def put(self, request, pk, format=None):
        # Buscar el objeto por ID
        unurseries = get_object_or_404(UserNurseries, pk=pk)
        
        # Obtener el nuevo estado desde el cuerpo de la solicitud
        newState = request.data.get('newState')

        # Validar que el estado sea válido (0 o 1)
        if newState is not None and newState in [0, 1]:
            # Actualizar el estado activo
            unurseries.activo = newState
            unurseries.save()
            
            # Serializar los datos actualizados
            serializer = UserNurseriesCreateSerializer(unurseries)
            return Response({
                'success': True,
                'message': 'Inventario actualizado!',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            # Manejar el caso de error
            return Response({
                'success': False,
                'message': 'Estado inválido proporcionado. Debe ser 0 o 1.',
                'errors': {'newState': 'Valor inválido. Asegúrate de enviar 0 o 1.'}
            }, status=status.HTTP_400_BAD_REQUEST)
