from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from .serializers import PageSerializer, PagesSerializer, SectionSerializer
from .models import Page, Pages, Section
from ..species.serializers import SpecieForrestSerializer, SpecieForrestTopSerializer
from django.db.models import F
from django.db import connection, transaction
from ..species.models import SpecieForrest
from rest_framework.exceptions import NotFound

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
        especie = SpecieForrest.objects.filter(cod_especie=code).first()
        if especie is None:
            return Response({'error': 'EspecieForestal no encontrada'}, status=404)

        especie.visitas += 1
        especie.save()

        serializer = SpecieForrestSerializer(especie)
        return Response(serializer.data)
    
class TopSpeciesView(APIView):
    def get(self, request, pk=None, format=None):
        queryset = SpecieForrest.objects.prefetch_related('images').order_by('-views')[:4]
        serializer = SpecieForrestTopSerializer(queryset, many=True)
        return Response(serializer.data)
            
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
    
    @transaction.atomic
    def post(self, request, format=None):
        adjusted_data = request.data.copy()

        # Validación de que los campos requeridos existen
        required_fields = ['router', 'title']
        if not all(field in adjusted_data for field in required_fields):
            return Response({"error": "Faltan campos requeridos."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PagesSerializer(data=adjusted_data)
        if serializer.is_valid():
            serializer.save()  # Utiliza el método save del serializador si es posible

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Respuesta detallada de los errores de validación
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    
    @transaction.atomic
    def post(self, request, format=None):
        adjusted_data = request.data.copy()

        # Validación de que los campos requeridos existen
        required_fields = ['page_id', 'section_title', 'content']
        if not all(field in adjusted_data for field in required_fields):
            return Response({"error": "Faltan campos requeridos."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SectionSerializer(data=adjusted_data)
        if serializer.is_valid():
            serializer.save()  # Utiliza el método save del serializador si es posible

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Respuesta detallada de los errores de validación
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        try:
            section = self.get_object(pk)
        except Http404:
            raise NotFound(detail="Sección no encontrada.", code=404)
        
        serializer = SectionSerializer(section, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        page = self.get_object(pk)
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)