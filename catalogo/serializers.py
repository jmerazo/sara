from rest_framework import serializers
from .models import EspecieForestal

class EspecieForestalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspecieForestal
        fields = '__all__'

class NombresComunesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspecieForestal
        fields = ['nom_comunes']

class FamiliaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspecieForestal
        fields = ['familia']

class NombreCientificoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspecieForestal
        fields = ['nombre_cientifico','nom_comunes', 'distribucion' ,'foto_general']