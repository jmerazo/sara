from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Glossary
from .serializers import GlossarySerializer

# VISTA GLOSARIO
class GlossaryView(APIView):
    def get(self, request, format=None): 
        queryset = Glossary.objects.all()
        serializer = GlossarySerializer(queryset, many=True)

        return Response(serializer.data)