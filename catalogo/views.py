from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import EspecieForestal
from .serializers import EspecieForestalSerializer, NombresComunesSerializer, FamiliaSerializer, NombreCientificoSerializer
from rest_framework.permissions import IsAuthenticated

class CurrentUser(viewsets.ModelViewSet):
     def get_queryset(self):
      user = self.request.user 
      return self.serializer_class.Meta.model.objects.filter(usuario=user)

class EspecieForestalView(viewsets.ModelViewSet):
   queryset = EspecieForestal.objects.all()
   serializer_class = EspecieForestalSerializer

class NombresComunesView(viewsets.ModelViewSet):
   queryset = EspecieForestal.objects.all()
   serializer_class = NombresComunesSerializer

class FamiliaView(viewsets.ModelViewSet):
   queryset = EspecieForestal.objects.all()
   serializer_class = FamiliaSerializer

class NombreCientificoView(viewsets.ModelViewSet):
   queryset = EspecieForestal.objects.all()
   serializer_class = NombreCientificoSerializer

class SuggestionTypeView(APIView):
    def get(self, request, types, format=None):
        if types == 'familia':
            queryset = EspecieForestal.objects.values_list('familia', flat=True)
        elif types == 'nom_comunes':
            queryset = EspecieForestal.objects.values_list('nom_comunes', flat=True)
        elif types == 'nombre_cientifico':
            queryset = EspecieForestal.objects.values_list('nombre_cientifico', flat=True)
        else:
            queryset = []

        return Response(list(queryset))

suggestion_type_view = SuggestionTypeView.as_view()

class BuscarEspecieView(APIView):
    def get(self, request, nombre, format=None):        
        search = EspecieForestal.objects.filter(nom_comunes__icontains=nombre).first()
        serializer = EspecieForestalSerializer(search)
        
        return Response(serializer.data)