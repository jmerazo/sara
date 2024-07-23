from rest_framework import serializers
from ..models import Users, Roles
from django.contrib.auth.hashers import make_password

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'

class UsersSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = [
            'id', 
            'email', 
            'password', 
            'first_name', 
            'last_name', 
            'rol', 
            'rol_id',
            'is_active', 
            'document_type', 
            'document_number', 
            'entity', 
            'cellphone', 
            'department', 
            'city',  
            'profession', 
            'reason', 
            'state', 
            'is_staff', 
            'last_login', 
            'is_superuser', 
            'date_joined'
        ]

    def create(self, validated_data):
        # Hash de la contraseña antes de guardarla en la base de datos
        validated_data['password'] = make_password(validated_data['password'])
        return super(UsersSerializer, self).create(validated_data)