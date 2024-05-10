from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from .serializers import NurseriesSerializer, UserNurseriesSerializer
from rest_framework.permissions import IsAuthenticated

from .models import Nurseries, UserNurseries

class NurseriesView(APIView):

    def get(self, request, pk=None, format=None):
        if pk:
            # Detalle específico de una instancia UserNurseries
            user_nursery = get_object_or_404(UserNurseries.objects.select_related('vivero__representante_legal', 'vivero', 'especie_forestal'), pk=pk)
            serializer = UserNurseriesSerializer(user_nursery)
            print('nurseries_user: ', user_nursery)
            print('serializer')
        else:
            # Lista de todas las instancias UserNurseries
            user_nurseries = UserNurseries.objects.select_related('vivero__representante_legal', 'vivero', 'especie_forestal').all()
            serializer = UserNurseriesSerializer(user_nurseries, many=True)
            print('user_nurseries: ', user_nurseries)
            print('data serializer: ', serializer.data)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = NurseriesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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