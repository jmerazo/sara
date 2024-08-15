from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.http import Http404
from django.db.models import F, Value
from django.db.models.functions import Concat

import random, string
from .models import Samples
from .serializers import SamplesSerializer, SamplesCreateSerializer
from rest_framework.permissions import IsAuthenticated

def generate_random_id(length):
            characters = string.ascii_letters + string.digits
            random_id = ''.join(random.choice(characters) for _ in range(length))
            return random_id
        
# VISTA MUESTRAS
class SamplesView(APIView):
    def get_queryset(self):
        queryset = Samples.objects.select_related(
            'user', 
            'evaluacion__cod_especie'
        ).annotate(
            numero_placa=F('evaluacion__numero_placa'),
            vernacularName=F('evaluacion__cod_especie__vernacularName'),
            nombre_cientifico=F('evaluacion__cod_especie__nombre_cientifico'),
            colector_full_name=Concat(
                F('user__first_name'),
                Value(' '),
                F('user__last_name')
            )
        )

        return queryset

    def get_object(self, pk=None):
        queryset = self.get_queryset()

        if pk is not None:
            try:
                sample = queryset.get(id=pk)
                return sample
            except Samples.DoesNotExist:
                raise Http404
        else:
            return queryset
        
    def get(self, request, pk=None, format=None):
        queryset = self.get_object(pk)

        serializer = SamplesSerializer(queryset, many=not pk)
        return Response(serializer.data)

    
    def post(self, request, format=None):
        serializer = SamplesCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format=None):
        sample = get_object_or_404(Samples, idmuestra=pk)
        serializer = SamplesCreateSerializer(sample, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        sample = get_object_or_404(Samples, idmuestra=pk)
        sample.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)