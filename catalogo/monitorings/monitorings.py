import random, string
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Monitorings
from ..candidates.models import CandidatesTrees
from .serializers import  MonitoringsSerializer

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
        queryset = Monitorings.objects.filter(
            evaluacion__numero_placa__isnull=False
        ).select_related(
            'evaluacion__cod_especie',  # Relación a la especie
            'user'  # Relación al usuario
        ).prefetch_related(
            'evaluacion'  # Pre-fetch de la relación de evaluación
        )

        return queryset

    def get(self, request, pk=None, format=None):
        queryset = self.get_queryset()

        if pk:
            queryset = queryset.filter(id=pk)

        serializer = MonitoringsSerializer(queryset, many=True)
        return Response(serializer.data)
    
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
