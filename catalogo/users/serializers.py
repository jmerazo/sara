from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from ..models import Users
from ..utils.models import Rol
from ..models import Departments, Cities

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
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    department = serializers.PrimaryKeyRelatedField(queryset=Departments.objects.all())
    city = serializers.PrimaryKeyRelatedField(queryset=Cities.objects.all())
    rol = serializers.PrimaryKeyRelatedField(queryset=Rol.objects.all())

    class Meta:
        model = Users
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.get('password')
        if password:
            validated_data['password'] = make_password(password)
        else:
            validated_data.pop('password', None)  # Eliminar password si está vacío
        return super().create(validated_data)

class UsersValidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'uuid_firebase', 'email', 'first_name', 'last_name', 'rol', 'is_active', 'verificated', 'date_joined']

class UserSendEmailMonitoring(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'email', 'first_name', 'last_name']