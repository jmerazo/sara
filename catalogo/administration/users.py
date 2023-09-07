from rest_framework import viewsets
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status, generics, permissions
from django.http import Http404
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from django.db.models import Q, Count
from decimal import Decimal
from ..models import Users
from ..serializers import UsersSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

class UsersView(APIView):
    def get_object(self, pk=None):
        if pk is not None:
            try:
                return Users.objects.get(pk=pk)
            except Users.DoesNotExist:
                raise Http404
        else:
            return Users.objects.all()

    def get(self, request, pk=None, format=None):
        users = self.get_object(pk)
        
        if isinstance(users, Users):
            serializer = UsersSerializer(users)
        else:
            serializer = UsersSerializer(users, many=True)
            
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = UsersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UsersSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)