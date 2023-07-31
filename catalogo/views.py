from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count
from decimal import Decimal

from .models import EspecieForestal, Glossary, CandidateTrees
from .serializers import EspecieForestalSerializer, NombresComunesSerializer, FamiliaSerializer, NombreCientificoSerializer, GlossarySerializer, GeoCandidateTreesSerializer, AverageTreesSerializer
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

class FamiliaView(viewsets.ViewSet):
    serializer_class = FamiliaSerializer

    #Aquí se realizó la función para enviar las familias sin duplicados
    def list(self, request, *args, **kwargs):
        queryset = EspecieForestal.objects.values('familia').distinct()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


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
    
class BuscarFamiliaView(APIView):
    def get(self, request, familia, format=None):        
        search = EspecieForestal.objects.filter(familia__icontains=familia)
        serializer = EspecieForestalSerializer(search, many=True)
        
        return Response(serializer.data)

class FamiliasView(APIView):
    def get(self, request, format=None):
        # Obtener las familias
        familias = EspecieForestal.objects.values('familia').annotate(total=Count('familia')).distinct()

        resultado = []

        # Recorrer las familias
        for familia in familias:
            familia_nombre = familia['familia']

            # Obtener las especies relacionadas a la familia actual
            especies = EspecieForestal.objects.filter(familia=familia_nombre)

            # Crear una lista de nombres de especies
            especies_nombres = [especie.nom_comunes for especie in especies]

            # Agregar la familia y las especies a la lista de resultados
            resultado.append({
                'familia': familia_nombre,
                'especies': especies_nombres
            })

        return Response(resultado)
    
class ScientificNameView(APIView):
    def get(self, request, scientific, format=None):        
        search = EspecieForestal.objects.filter(nombre_cientifico__icontains=scientific).first()
        serializer = EspecieForestalSerializer(search)
        
        return Response(serializer.data)

class GlossaryView(APIView):
    def get(self, request, format=None): 
        queryset = Glossary.objects.all()
        serializer = GlossarySerializer(queryset, many=True)

        return Response(serializer.data)
    
class GeoCandidateTreesView(APIView):
    def get(self, request, format=None): 
        geo = CandidateTrees.objects.all()
        geoData = GeoCandidateTreesSerializer(geo, many=True).data

        geo_format = []

        for datos in geoData:
            latitud, longitud  = datos['abcisa_xy'].split(', ')
            code_number = int(datos['cod_especie'])
            geo_fixed = {'codigo': code_number, 'lat': float(latitud), 'lon': float(longitud)}
            geo_format.append(geo_fixed)

        """ print('Coordendas', geo_format) """
        return Response(geo_format)

class AverageCandidateTreesView(APIView):
    def convert_to_decimal_or_int(self, value):
        try:
            return Decimal(value)
        except (TypeError, ValueError):
            try:
                return int(value)
            except (TypeError, ValueError):
                return None

    def get(self, request, format=None): 
        average = CandidateTrees.objects.all()
        averageData = AverageTreesSerializer(average, many=True).data

        average_format = []

        for datos in averageData:
            code_number = self.convert_to_decimal_or_int(datos['altura_comercial'])

            altura_total_str = datos['altura_total']
            at = self.convert_to_decimal_or_int(altura_total_str)

            altura_ccial_str = datos['altura_comercial']
            ac = self.convert_to_decimal_or_int(altura_ccial_str)

            average_fixed = {'codigo': code_number, 'altura_total': at, 'altura_comercial': ac, 'cobertura': datos['cobertura']}
            average_format.append(average_fixed)

        return Response(average_format)