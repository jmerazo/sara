from rest_framework.response import Response
from django.db.models import Prefetch
from rest_framework.views import APIView
from ..models import EspecieForestal, ImagesSpeciesRelated
from ..serializers import EspecieForestalSerializer
from django.db import connection

class UpdateCountVisitsView(APIView):
    def get(self, request, code, format=None):
        especie = EspecieForestal.objects.filter(cod_especie=code).first()
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
