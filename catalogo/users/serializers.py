from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from ..models import Users
from ..models import Departments, Cities
from ..serializers import DepartmentsSerializer, CitiesSerializer
from ..utils.models import Rol

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

class UsersSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = '__all__'

    def create(self, validated_data):
        # Hash de la contraseña antes de guardarla en la base de datos
        validated_data['password'] = make_password(validated_data['password'])
        return super(UsersSerializer, self).create(validated_data)
    
class UsersCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    department = serializers.PrimaryKeyRelatedField(queryset=Departments.objects.all())
    city = serializers.PrimaryKeyRelatedField(queryset=Cities.objects.all())
    rol = serializers.PrimaryKeyRelatedField(queryset=Rol.objects.all())

    class Meta:
        model = Users
        fields = '__all__'

    def create(self, validated_data):
        # Hash de la contraseña antes de guardarla en la base de datos
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)