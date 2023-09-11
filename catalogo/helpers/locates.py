from rest_framework import viewsets
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status, generics, permissions
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from django.db.models import Count, OuterRef, Subquery
from datetime import datetime
from collections import defaultdict
from calendar import monthrange
from django.db import connection

from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

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