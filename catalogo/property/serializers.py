from rest_framework import serializers
from .models import Property, UserPropertyFile

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'

class UserPropertyFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPropertyFile
        fields = '__all__'