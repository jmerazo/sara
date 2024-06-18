from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Departments, Cities
from ..serializers import DepartmentsSerializer, CitiesSerializer

class DepartmentsView(APIView):
    def get(self, request, format=None): 
        queryset = Departments.objects.all()
        serializer = DepartmentsSerializer(queryset, many=True)

        return Response(serializer.data)
    
class CitiesView(APIView):
    def get(self, request, format=None): 
        queryset = Cities.objects.all()
        serializer = CitiesSerializer(queryset, many=True)

        return Response(serializer.data)