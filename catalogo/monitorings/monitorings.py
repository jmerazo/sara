from django.db import connection
from rest_framework import status
from django.db.models import Q, Prefetch
from rest_framework.views import APIView
from django.db import DatabaseError
from rest_framework.exceptions import APIException
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django.template.loader import render_to_string
from ..helpers.Email import send_email

from .models import Monitorings
from ..candidates.models import CandidatesTrees
from ..species.models import SpecieForrest
from .serializers import  MonitoringsSerializer, MonitoringCreateSerializer
from ..users.serializers import UserSendEmailMonitoring

class MonitoringsPagination(PageNumberPagination):
    page_size = 50  # Tamaño de página predeterminado
    page_size_query_param = 'page_size'  # Permitir que el tamaño de página sea dinámico
    max_page_size = 1000  # Límite máximo de datos por página

    def get_paginated_response(self, data):
        return Response({
            'results': data,
            'total_items': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'current_page': self.page.number,  # Página actual
            'total_pages': self.page.paginator.num_pages,  # Total de páginas
        })

# VISTAS MONITOREOS
class SearchMonitoringCandidateView(APIView):
    def get(self, request, id, format=None):
        sql = """
            SELECT 
            ea.id,
            ea.numero_placa,
            ea.cod_expediente,
            ea.cod_especie_id,
            u.id,
            u.first_name,
            u.last_name,
            ef.id,
            ef.habit,
            ef.vernacularName,
            ef.nombre_cientifico,
            m.* 
            FROM monitoreo_c AS m
            INNER JOIN evaluacion_as_c as ea ON ea.id = m.evaluacion_id
            INNER JOIN Users as u ON u.id = m.user_id
            INNER JOIN especie_forestal_c AS ef ON ef.code_specie = ea.cod_especie_id
            WHERE evaluacion_id = %s;
        """
        
        with connection.cursor() as cursor:
            cursor.execute(sql, [id])
            result = cursor.fetchall()

            if not result:
                return Response({
                    'success': False,
                    'message': 'No se encontraron datos para este ID'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Obtén los nombres de las columnas y organiza los resultados
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in result]
        
            return Response({
                'success': True,
                'message': 'Consulta realizada con éxito',
                'data': data
            })

class SearchMonitoringSpecieView(APIView):
    def get(self, request, code, format=None):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    m.*
                FROM 
                    monitoreo_c AS m
                INNER JOIN 
                    evaluacion_as_c AS ea ON m.evaluacion_id = ea.id
                WHERE 
                    ea.cod_especie_id = %s;
            """, [code])
            
            columns = [col[0] for col in cursor.description]
            result = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        
        return Response(result)

class MonitoringsView(APIView):
    def get_queryset(self):
        try:
            queryset = Monitorings.objects.filter(
                evaluacion__numero_placa__isnull=False
            ).select_related(
                'evaluacion__cod_especie',
                'user'
            ).prefetch_related(
                Prefetch('evaluacion', queryset=CandidatesTrees.objects.all()),
                Prefetch('evaluacion__cod_especie', queryset=SpecieForrest.objects.all())
            ).order_by('-fecha_monitoreo')

            # Obtener el término de búsqueda desde los parámetros de consulta
            search_term = self.request.GET.get('search', '').strip()
            if search_term:
                queryset = queryset.filter(
                    Q(evaluacion__numero_placa__icontains=search_term) |
                    Q(evaluacion__cod_especie__vernacularName__icontains=search_term) |
                    Q(evaluacion__cod_especie__scientificName__icontains=search_term) |
                    Q(evaluacion__cod_especie__scientificNameAuthorship__icontains=search_term) |
                    Q(evaluacion__cod_especie__nombre_cientifico__icontains=search_term)
                )

            return queryset

        except ObjectDoesNotExist as e:
            raise APIException(f"Error: No se encontraron objetos - {str(e)}")
        except DatabaseError as e:
            raise APIException(f"Error en la base de datos: {str(e)}")
        except Exception as e:
            raise APIException(f"Error inesperado en get_queryset: {str(e)}")

    def get(self, request, pk=None, format=None):
        try:
            queryset = self.get_queryset()
            paginator = MonitoringsPagination()

            if queryset.exists():
                page = paginator.paginate_queryset(queryset, request)
                if page is not None:
                    serializer = MonitoringsSerializer(page, many=True)
                    return paginator.get_paginated_response(serializer.data)

            serializer = MonitoringsSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except APIException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"Error inesperado en la vista: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, format=None):
        serializer = MonitoringCreateSerializer(data=request.data)
        if serializer.is_valid():
            monitoring = serializer.save()

            # Obtener los datos del usuario
            user_data = UserSendEmailMonitoring(monitoring.user_id).data
            usuario_registrador = f"{user_data['first_name']} {user_data['last_name']}"
            usuario_email = user_data['email']

            # Preparar el diccionario de datos para el template (sin espacios en las claves)
            email_context = {
                'fecha_monitoreo': monitoring.fecha_monitoreo,
                'hora': monitoring.hora,
                'ubicacion_actual': monitoring.ubicacion_actual,
                'validacion_ubicacion': monitoring.validacion_ubicacion,
                'precipitacion': monitoring.precipitacion,
                **{
                    # Solo se incluirán las claves cuyo valor no sea None
                    key.replace('.', '_').replace(' ', '_'): value
                    for key, value in {
                        'estado_sanitario_palma': monitoring.estado_sanitario_palma,
                        'estado_fisico_tallo': monitoring.estado_fisico_tallo,
                        'factores_amenaza_individuos': monitoring.factores_amenaza_individuos,
                        'cant_racimos_capuchon': monitoring.cant_racimos_capuchon,
                        'cant_racimos_flores': monitoring.cant_racimos_flores,
                        'cant_racimos_frutos_verdes': monitoring.cant_racimos_frutos_verdes,
                        'cant_racimos_frutos_maduros': monitoring.cant_racimos_frutos_maduros,
                        'cant_racimos_senescente': monitoring.cant_racimos_senescente,
                        'peso_racimo_completo': monitoring.peso_racimo_completo,
                        'peso_frutos_desgranados': monitoring.peso_frutos_desgranados,
                        'cant_frutos_por_racimo': monitoring.cant_frutos_por_racimo,
                        'cantidad_anillos_tallo': monitoring.cantidad_anillos_tallo,
                        'cobertura': monitoring.cobertura, 
                        'altura_total': monitoring.altura_total,
                        'altura_del_fuste': monitoring.altura_del_fuste,
                        'eje_x': monitoring.eje_x,
                        'eje_y': monitoring.eje_y,
                        'eje_z': monitoring.eje_z,
                        'follaje': monitoring.follaje,
                        'follaje_porcentaje': monitoring.follaje_porcentaje,
                        'flor_abierta': monitoring.flor_abierta,
                        'color_flor': monitoring.color_flor,
                        'fauna_flor': monitoring.fauna_flor,
                        'frutos_verdes': monitoring.frutos_verdes,
                        'estado_madurez_frutos_verdes': monitoring.estado_madurez_frutos_verdes,
                        'estado_madurez_frutos_maduros': monitoring.estado_madurez_frutos_maduros,
                        'estado_madurez_frutos_pintones': monitoring.estado_madurez_frutos_pintones,
                        'estado_madurez_frutos': monitoring.estado_madurez_frutos,
                        'color_fruto': monitoring.color_fruto,
                        'cantidad_frutos_rama': monitoring.cantidad_frutos_rama,
                        'cant_ramas_fraccion_copa': monitoring.cant_ramas_fraccion_copa,
                        'porcentaje_fraccion_copa': monitoring.porcentaje_fraccion_copa,
                        'cantidad_frutos_arbol': monitoring.cantidad_frutos_arbol,
                        'medida_peso_frutos': monitoring.medida_peso_frutos,
                        'largo_fruto_maximo': monitoring.largo_fruto_maximo,
                        'ancho_fruto_maximo': monitoring.ancho_fruto_maximo,
                        'largo_fruto_minimo': monitoring.largo_fruto_minimo,
                        'ancho_fruto_minimo': monitoring.ancho_fruto_minimo,
                        'peso_frutos': monitoring.peso_frutos,
                        'cantidad_frutos_medidos': monitoring.cantidad_frutos_medidos,
                        'peso_por_fruto': monitoring.peso_por_fruto,
                        'fauna_frutos': monitoring.fauna_frutos,
                        'cant_semillas': monitoring.cant_semillas,
                        'medida_peso_sem': monitoring.medida_peso_sem,
                        'peso_semillas': monitoring.peso_semillas,
                        'cantidad_semillas_medidos': monitoring.cantidad_semillas_medidos,
                        'peso_por_semilla': monitoring.peso_por_semilla,
                        'cant_semillas_por_arbol': monitoring.cant_semillas_por_arbol,
                        'largo_semilla_maximo': monitoring.largo_semilla_maximo,
                        'ancho_semilla_maximo': monitoring.ancho_semilla_maximo,
                        'largo_semilla_minimo': monitoring.largo_semilla_minimo,
                        'ancho_semila_minimo': monitoring.ancho_semila_minimo,
                        'observaciones': monitoring.observaciones
                    }.items() if value is not None
                }
            }

            # Renderizar el contenido HTML del correo
            html_content = render_to_string(
                "monitorings.html", 
                {
                    'usuario_registrador': usuario_registrador,
                    'email_context': email_context
                }
            )

            # Adjuntar el logo (asegurarse de que la ruta sea la correcta)
            attachments = []
            try:
                with open('catalogo/helpers/resources/imgs/sara.png', 'rb') as f:
                    # El nombre del archivo se usará como Content-ID para la imagen inline
                    logo = ('sara.png', f.read(), 'image/png')
                    attachments.append(logo)
            except FileNotFoundError:
                print("Logo file not found. Email will be sent without the logo.")

            # Preparar y enviar el correo
            subject = f"Nuevo Monitoreo Registrado por {usuario_registrador}"
            body = "Detalles del monitoreo registrados en el sistema."
            recipients = ['jmerazo96@gmail.com', usuario_email]

            for email in recipients:
                send_email(subject, body, email, html_content=html_content, attachments=attachments)

            return Response({
                'success': True,
                'message': 'Monitoreo creado con éxito!',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'message': 'Error al crear el monitoreo',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format=None):
        monitoring = get_object_or_404(Monitorings, id=pk)
        serializer = MonitoringCreateSerializer(monitoring, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Monitoreo actualizado con éxito!',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'message': 'Error al actualizar el monitoreo',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        monitoring = get_object_or_404(Monitorings, id=pk)
        monitoring.delete()
        return Response({
            'success': True,
            'message': 'Monitoreo eliminado con éxito!'
        }, status=status.HTTP_204_NO_CONTENT)

class MonitoringsUserView(APIView):
    def get_queryset(self, user):
        queryset = Monitorings.objects.filter(
            evaluacion__numero_placa__isnull=False,
            user_id=user
        ).select_related(
            'user', 'evaluacion__cod_especie'
        )
        return queryset

    def get(self, request, user_id, format=None):
        queryset = self.get_queryset(user_id)
        serializer = MonitoringsSerializer(queryset, many=True)
        return Response(serializer.data)
    
class DownloadMonitoringsView(APIView):
    def get_queryset(self):
        sql_query = """
            SELECT u.id, ea.numero_placa, u.first_name, u.last_name, ef.vernacularName, 
                   ef.scientificName, ef.scientificNameAuthorship, ef.code_specie, m.*
            FROM monitoreo_c AS m
            INNER JOIN Users AS u ON u.id = m.user_id
            INNER JOIN evaluacion_as_c AS ea ON ea.id = m.evaluacion_id
            INNER JOIN especie_forestal_c AS ef ON ef.code_specie = ea.cod_especie_id
            WHERE ea.numero_placa IS NOT NULL
            ORDER BY m.fecha_monitoreo;
        """
        
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()

        # Convierte los resultados a una lista de diccionarios para facilitar el retorno en JSON
        data = [dict(zip(columns, row)) for row in results]
        return data

    def get(self, request, format=None):
        # Obtiene la lista de diccionarios con la data de la consulta SQL
        data = self.get_queryset()
        
        # Devuelve los datos como JSON
        return Response(data)