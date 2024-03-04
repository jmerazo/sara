from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from .models import EmpiricalKnowledge
from .serializers import EmpiricalKnowledgeSerializer
from rest_framework.permissions import IsAuthenticated

class EmpiricalKnowledgeView(APIView):
    def get(self, request, pk=None, format=None): 
        if pk:
            # Obtener un objeto específico por pk
            queryset = EmpiricalKnowledge.objects.filter(id=pk)
        else:
            queryset = EmpiricalKnowledge.objects.exclude(numero_placa__isnull=True)

        serializer = EmpiricalKnowledgeSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = EmpiricalKnowledgeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format=None):
        ek = get_object_or_404(EmpiricalKnowledge, pk=pk)
        serializer = EmpiricalKnowledgeSerializer(ek, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        ek = get_object_or_404(EmpiricalKnowledge, pk=pk)
        ek.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)