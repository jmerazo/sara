from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from .serializers import PageSerializer, PagesSerializer, SectionSerializer
from .models import Page, Pages, Section
from ..species.serializers import EspecieForestalSerializer
from django.db import connection
from ..species.models import specieForrest

# VISTA PÁGINA ACERCA OTROS            
class PageView(APIView):
    def get_object(self, pk=None):
        if pk is not None:
            try:
                return Page.objects.get(pk=pk)
            except Page.DoesNotExist:
                raise Http404
        else:
            return Page.objects.all()

    def get(self, request, pk=None, format=None):
        pages = self.get_object(pk)
        
        if isinstance(pages, Page):
            serializer = PageSerializer(pages)
        else:
            serializer = PageSerializer(pages, many=True)
            
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        page = self.get_object(pk)
        serializer = PageSerializer(page, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        page = self.get_object(pk)
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UpdateCountVisitsView(APIView):
    def get(self, request, code, format=None):
        especie = specieForrest.objects.filter(cod_especie=code).first()
        if especie is None:
            return Response({'error': 'EspecieForestal no encontrada'}, status=404)

        especie.visitas += 1
        especie.save()

        serializer = EspecieForestalSerializer(especie)
        return Response(serializer.data)
    
class topSpeciesView(APIView):
    def get(self, request, pk=None, format=None):
        query = """
            SELECT ef.cod_especie, ef.nom_comunes, i.img_general, ef.visitas 
            FROM especie_forestal AS ef 
            LEFT JOIN img_species AS i ON ef.ShortcutID = i.specie_id
            ORDER BY ef.visitas DESC
            LIMIT 4;
        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            try:
                rows = cursor.fetchall()
                if rows:
                    columns = [col[0] for col in cursor.description]

                    # Procesar los datos obtenidos de la consulta SQL personalizada
                    species_data = []
                    for row in rows:
                        data = {}
                        for col, value in zip(columns, row):
                            data[col] = value
                        species_data.append(data)

                    return Response(species_data)  # Devuelve directamente los datos obtenidos
                else:
                    return Response([])  # Devuelve una lista vacía si no hay resultados
            except Exception as e:
                return Response({"error": str(e)})  # Devuelve un mensaje de error en caso de excepción
            
class PagesView(APIView):
    def get_object(self, pk=None):
        if pk is not None:
            try:
                return Pages.objects.get(pk=pk)
            except Pages.DoesNotExist:
                raise Http404
        else:
            return Pages.objects.all()

    def get(self, request, pk=None, format=None):
        pages = self.get_object(pk)
        
        if isinstance(pages, Pages):
            serializer = PagesSerializer(pages)
        else:
            serializer = PagesSerializer(pages, many=True)
            
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        page = self.get_object(pk)
        serializer = PagesSerializer(page, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        page = self.get_object(pk)
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class SectionView(APIView):
    def get_object(self, pk=None):
        if pk is not None:
            try:
                return Section.objects.get(pk=pk)
            except Section.DoesNotExist:
                raise Http404
        else:
            return Section.objects.all()

    def get(self, request, pk=None, format=None):
        sections = self.get_object(pk)
        
        if isinstance(sections, Section):
            serializer = SectionSerializer(sections)
        else:
            serializer = SectionSerializer(sections, many=True)
            
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        page = self.get_object(pk)
        serializer = SectionSerializer(page, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        page = self.get_object(pk)
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)