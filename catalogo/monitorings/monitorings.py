import random, string
from rest_framework import status
from django.core.cache import cache
from django.db.models import Prefetch
from rest_framework.views import APIView
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
        return Monitorings.objects.filter(
            evaluacion__numero_placa__isnull=False
        ).select_related(
            'evaluacion__cod_especie',
            'user'
        ).prefetch_related(
            Prefetch('evaluacion', queryset=CandidatesTrees.objects.all()),
            Prefetch('evaluacion__cod_especie', queryset=SpecieForrest.objects.all())
        )

    def get(self, request, pk=None, format=None):
        cache_key = f"monitorings_{pk if pk else 'all'}"
        result = cache.get(cache_key)

        if result is None:
            queryset = self.get_queryset()

            if pk:
                queryset = queryset.filter(id=pk)

            serializer = MonitoringsSerializer(queryset, many=True)
            result = serializer.data

            # Cachear el resultado por un tiempo apropiado (ajusta según tus necesidades)
            cache.set(cache_key, result, 300)  # 300 segundos = 5 minutos

        return Response(result)
    
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
