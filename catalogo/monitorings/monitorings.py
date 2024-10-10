import random, string
from rest_framework import status
from django.core.cache import cache
from django.db.models import Prefetch
from rest_framework.views import APIView
from django.core.paginator import Paginator
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Monitorings, ViewMonitorings
from ..candidates.models import CandidatesTrees
from ..species.models import SpecieForrest
from .serializers import  MonitoringsSerializer, ViewMonitoringsSerializer

def generate_random_id(length):
            characters = string.ascii_letters + string.digits
            random_id = ''.join(random.choice(characters) for _ in range(length))
            return random_id

# VISTAS MONITOREOS
class SearchMonitoringCandidateView(APIView):
    def get(self, request, id, format=None):        
        search = Monitorings.objects.filter(ShortcutIDEV=id)
        serializer = MonitoringsSerializer(search, many=True)
        
        return Response(serializer.data)

class SearchMonitoringSpecieView(APIView):
    def get(self, request, code, format=None):
        # Obtener los valores de ShortcutIDEV desde la subconsulta
        shortcut_idevs = CandidatesTrees.objects.filter(cod_especie=code).values('ShortcutIDEV')
        
        # Realizar la búsqueda en la tabla Monitoring usando esos valores
        search = Monitorings.objects.filter(ShortcutIDEV__in=shortcut_idevs)
        
        serializer = MonitoringsSerializer(search, many=True)
        
        return Response(serializer.data)

class MonitoringsView(APIView):
    def get_queryset(self):
        # Filtro base
        queryset = Monitorings.objects.filter(
            evaluacion__numero_placa__isnull=False
        ).select_related(
            'evaluacion__cod_especie',
            'user'
        ).prefetch_related(
            Prefetch('evaluacion', queryset=CandidatesTrees.objects.all()),
            Prefetch('evaluacion__cod_especie', queryset=SpecieForrest.objects.all())
        )
        
        # Filtro de búsqueda global
        search_term = self.request.query_params.get('search', None)
        if search_term:
            queryset = queryset.filter(evaluacion__numero_placa__icontains=search_term)
        
        return queryset

    def get(self, request, pk=None, format=None):
        # Obtener el queryset completo de acuerdo con el término de búsqueda
        queryset = self.get_queryset()
        
        # Configurar paginación a nivel de backend
        page_size = int(request.query_params.get('page_size', 50))  # Tamaño de página ajustable
        page_number = int(request.query_params.get('page', 1))  # Página solicitada
        paginator = Paginator(queryset, page_size)  # Paginador con el queryset completo
        page = paginator.get_page(page_number)  # Obtener la página solicitada

        # Serializar la página actual
        serializer = MonitoringsSerializer(page, many=True)

        # Obtener total de elementos y páginas
        total_items = paginator.count
        total_pages = paginator.num_pages

        # Respuesta con datos paginados
        return Response({
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page_number,
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        serializer = MonitoringsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format=None):
        monitoring = get_object_or_404(Monitorings, IDmonitoreo=pk)
        serializer = MonitoringsSerializer(monitoring, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        monitoring = get_object_or_404(Monitorings, IDmonitoreo=pk)
        monitoring.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
