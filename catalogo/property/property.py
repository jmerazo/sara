import hashlib
from datetime import date
from random import randint
from django.db import models, transaction
from django.db import connection, connections
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, F, Subquery, OuterRef, IntegerField
from .serializers import PropertySerializer, UserPropertyFileSerializer, UserPropertyFileAllSerializer, MonitoringPropertySerializer, PropertyCreateSerializer, SpeciesRecordSerializer, SpeciesRecordCreateSerializer

from .models import Property, UserPropertyFile, SpeciesRecord
from ..monitorings.models import Monitorings
from ..species.models import SpecieForrest
from ..candidates.models import CandidatesTrees
from ..candidates.serializers import CandidateTreesCreateSerializer, CandidateTreesSerializer

class PropertyView(APIView):
    def get(self, request, pk=None, format=None):
        # Filtrar por 'pk' si se proporciona, de lo contrario obtener todos los registros
        if pk:
            queryset = Property.objects.filter(id=pk).select_related('p_user', 'p_departamento', 'p_municipio')
        else:
            queryset = Property.objects.all().select_related('p_user', 'p_departamento', 'p_municipio')

        # Serializar los datos
        serializer = PropertySerializer(queryset, many=True)

        # Retornar la respuesta en formato JSON
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = PropertyCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'msg': 'Propiedad creada exitosamente.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'msg': 'Error al crear la propiedad.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        nurseries = get_object_or_404(Property, pk=pk)
        serializer = PropertyCreateSerializer(nurseries, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'msg': 'Propiedad actualizada exitosamente.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'msg': 'Error al actualizar la propiedad.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        nurseries = get_object_or_404(Property, pk=pk)
        nurseries.delete()
        return Response({
            'success': True,
            'msg': 'Propiedad eliminada exitosamente.'
        }, status=status.HTTP_204_NO_CONTENT)
    
class PropertyUserIdView(APIView):
    def get(self, request, pk=None, format=None):
        if pk:
            queryset = Property.objects.filter(p_user_id=pk).select_related(
                'p_user', 'p_departamento', 'p_municipio'
            ).values(
                'id',
                'p_user__first_name',
                'p_user__last_name',
                'nombre_predio',
                'p_departamento__name',
                'p_municipio__name'
            )

        # Procesar los resultados para convertirlos en una lista de diccionarios
        predios = list(queryset)

        # Retornar la respuesta en formato JSON
        return Response(predios, status=status.HTTP_200_OK)
    
class UserPropertyFileView(APIView):
    def get(self, request, pk=None, format=None):
        sql_query = """
            WITH ranked_species AS (
                SELECT ee.expediente_id, ee.ep_especie_id, ee.cantidad_autorizada, ee.cantidad_remanentes, 
                       ee.cantidad_aprovechable, ee.CM, ee.RM, ee.cantidad_placas,
                       ROW_NUMBER() OVER (PARTITION BY ee.expediente_id ORDER BY ee.ep_especie_id) AS rn
                FROM especies_expediente AS ee
            )
            SELECT up.id, up.expediente, up.resolucion, up.fecha_exp, up.ep_usuario_id, up.ep_predio_id, 
                   p.nombre_predio, dp.name AS departamento, c.name AS municipio,
                   rs.ep_especie_id, ef.vernacularName, ef.scientificName, ef.scientificNameAuthorship, 
                   rs.cantidad_autorizada, rs.cantidad_remanentes, rs.cantidad_aprovechable, 
                   rs.CM, rs.RM, rs.cantidad_placas
            FROM usuario_expediente_predio AS up
            LEFT JOIN ranked_species AS rs ON rs.expediente_id = up.id AND rs.rn = 1
            LEFT JOIN especie_forestal_c AS ef ON ef.code_specie = rs.ep_especie_id
            LEFT JOIN predios AS p ON p.id = up.ep_predio_id
            LEFT JOIN departments AS dp ON dp.id = p.p_departamento_id
            LEFT JOIN cities AS c ON c.id = p.p_municipio_id
        """

        params = []
        if pk:
            sql_query += " WHERE up.ep_usuario_id = %s"
            params.append(pk)

                
        with connections['default'].cursor() as cursor:
            cursor.execute(sql_query, params)
            results = [
                dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()
            ]

        return Response(results, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = UserPropertyFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'msg': 'Especie asignada satisfactoriamente.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'msg': 'Error al asignar la especie.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        u_property = get_object_or_404(UserPropertyFile, pk=pk)
        serializer = UserPropertyFileSerializer(u_property, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'msg': 'Especie actualizada satisfactoriamente.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'msg': 'Error al actualizar la especie.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        u_property = get_object_or_404(UserPropertyFile, pk=pk)
        u_property.delete()
        return Response({
            'success': True,
            'msg': 'Especie eliminada satisfactoriamente.'
        }, status=status.HTTP_204_NO_CONTENT)
    
class MonitoringPropertyView(APIView):
    def get(self, request, format=None):
        # Definir la subconsulta para contar los monitoreos relacionados al usuario
        start_date = date(2024, 1, 1)

        subquery = Monitorings.objects.filter(
            user_id=OuterRef('ep_usuario_id'),
            evaluacion__cod_especie_id=OuterRef('ep_especie_id'),
            fecha_monitoreo__range=(start_date, date.today())
        ).values('user_id').annotate(
            cant_monitoreos_r=Count('id')
        ).values('cant_monitoreos_r')

        # Realizar la consulta principal con las anotaciones
        queryset = UserPropertyFile.objects.annotate(
            cant_monitoreos_r=Subquery(subquery, output_field=IntegerField()),
            diferencia_monitoreos=F('cant_monitoreos') - Subquery(subquery, output_field=IntegerField(), default=0)
        ).all()

        # Serializar los datos con el serializador actualizado
        serializer = MonitoringPropertySerializer(queryset, many=True)
        return Response(serializer.data)
    
class PropertyRecordSearchView(APIView):
    def get(self, request, pk, format=None):
        try:
            query = """
            SELECT * FROM usuario_expediente_predio
            WHERE ep_usuario_id = %s;
            """
            with connection.cursor() as cursor:
                cursor.execute(query, [pk])
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({
                'success': True,
                'msg': 'Consulta ejecutada correctamente.',
                'data': results
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'success': False,
                'msg': f'Error al ejecutar la consulta: {str(e)}',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class SpeciesRecordView(APIView):
    def get(self, request, pk=None, format=None):
        if pk:
            queryset = SpeciesRecord.objects.filter(ep_usuario_id=pk)
        else:
            queryset = SpeciesRecord.objects.all()

        serializer = SpeciesRecordSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        # Obtener datos obligatorios desde request.data
        expediente = request.data.get('expediente')
        ep_especie = request.data.get('ep_especie')
        
        if not all([expediente, ep_especie]):
            return Response({
                'success': False,
                'msg': 'Faltan datos obligatorios.',
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Intentar convertir a enteros los campos numéricos
        try:
            cantidad_placas = int(request.data.get('cantidad_placas', 0))
            cm = int(request.data.get('CM', 0))
            rm = int(request.data.get('RM', 0))
        except (TypeError, ValueError):
            return Response({
                'success': False,
                'msg': 'Los valores numéricos son inválidos.',
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validación básica de los datos numéricos
        if (cantidad_placas <= 0) or (cm < 0) or (rm < 0):
            return Response({
                'success': False,
                'msg': f"Datos inválidos para la especie con ID {ep_especie}.",
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Preparar los datos para el serializer
        dataRecord = {
            'expediente': expediente,
            'ep_especie': ep_especie,
            'cantidad_autorizada': request.data.get('cantidad_autorizada'),
            'cantidad_remanentes': request.data.get('cantidad_remanentes'),
            'cantidad_aprovechable': request.data.get('cantidad_aprovechable'),
            'CM': cm,
            'RM': rm,
            'cantidad_placas': cantidad_placas
        }
        print('data records ', dataRecord)
        
        try:
            # Abrir una transacción atómica para asegurar que ambos procesos se ejecuten o se reviertan juntos
            with transaction.atomic():
                # Insertar en SpeciesRecord
                serializer = SpeciesRecordCreateSerializer(data=dataRecord)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response({
                        'success': False,
                        'msg': 'Error en la validación de los datos de la especie.',
                        'errors': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Validar y obtener el hábito de la especie
                try:
                    especie_obj = SpecieForrest.objects.get(code_specie=ep_especie)
                    habito = especie_obj.habit.lower() if especie_obj.habit else None
                except SpecieForrest.DoesNotExist:
                    return Response({
                        'success': False,
                        'msg': f"Especie no encontrada (ID: {ep_especie}).",
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if not habito:
                    return Response({
                        'success': False,
                        'msg': f"Hábito desconocido para la especie (ID: {ep_especie}).",
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Definir prefijos según el hábito
                if habito == 'árbol':
                    prefixes = ['ACM', 'ARM', 'ARN']
                elif habito == 'palma':
                    prefixes = ['PCM', 'PRM', 'PRN']
                else:
                    return Response({
                        'success': False,
                        'msg': f"Hábito desconocido para la especie (ID: {ep_especie}).",
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Obtener el último número de placa
                last_placa = CandidatesTrees.objects.aggregate(last_placa=models.Max('numero_placa'))['last_placa'] or 0
                counter = 0
                prefix_counters = [0, 0, 0]  # Contadores para cada prefijo
                
                # Crear las placas en CandidatesTrees
                while counter < cantidad_placas:
                    new_placa = last_placa + counter + 1
        
                    # Generar un ID único aleatorio
                    while True:
                        random_id = hashlib.md5(str(randint(1, 1000000)).encode()).hexdigest()[:8]
                        if not CandidatesTrees.objects.filter(id=random_id).exists():
                            break
        
                    # Determinar el prefijo del identificador basado en los contadores y límites (CM y RM)
                    if prefix_counters[0] < cm:
                        prefix_counters[0] += 1
                        identificador = f"{prefixes[0]}-{prefix_counters[0]}"
                    elif prefix_counters[1] < rm:
                        prefix_counters[1] += 1
                        identificador = f"{prefixes[1]}-{prefix_counters[1]}"
                    else:
                        prefix_counters[2] += 1
                        identificador = f"{prefixes[2]}-{prefix_counters[2]}"
        
                    dataCandidates = {
                        'id': random_id,
                        'numero_placa': new_placa,
                        'cod_expediente': request.data.get('code_expediente'),
                        'cod_especie_id': ep_especie,
                        'user_id': request.data.get('ep_usuario'),
                        'property_id': request.data.get('ep_predio'),
                        'identificador': identificador,
                        'validated': 'Por evaluar'
                    }
        
                    # Crear la placa
                    CandidatesTrees.objects.create(**dataCandidates)
                    counter += 1
                
            # Si todo sale bien, se confirma la transacción y se retorna la respuesta correcta
            return Response({
                'success': True,
                'msg': 'Especie asignada correctamente',
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            # En caso de cualquier excepción, se revierte la transacción completa
            return Response({
                'success': False,
                'msg': f'Error al asignar la especie: {str(e)}',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk, format=None):
        species_record = get_object_or_404(SpeciesRecord, pk=pk)
        serializer = SpeciesRecordCreateSerializer(species_record, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'msg': 'Expediente especie actualizada satisfactoriamente.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'msg': 'Error al actualizar la especie.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        species_record = get_object_or_404(SpeciesRecord, pk=pk)
        species_record.delete()
        return Response({
            'success': True,
            'msg': 'Expediente especie eliminada satisfactoriamente.'
        }, status=status.HTTP_204_NO_CONTENT)