from rest_framework import serializers
from .models import Property, UserPropertyFile
from ..serializers import DepartmentsSerializer, CitiesSerializer
from ..models import Users
from ..species.models import SpecieForrest

class PropertyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'first_name', 'last_name']

class PropertySerializer(serializers.ModelSerializer):
    p_user = PropertyUserSerializer()  # Cambia 'user' a 'p_user'
    p_departamento = DepartmentsSerializer()
    p_municipio = CitiesSerializer()

    class Meta:
        model = Property
        fields = '__all__'

class SpecieForrestPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecieForrest
        fields = ['id', 'vernacularName', 'scientificName', 'scientificNameAuthorship']

class UserPropertyFileAllSerializer(serializers.ModelSerializer):
    ep_especie = SpecieForrestPropertySerializer()
    ep_usuario = PropertyUserSerializer()
    ep_predio = PropertySerializer()

    class Meta:
        model = UserPropertyFile
        fields = '__all__'

class UserPropertyFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPropertyFile
        fields = '__all__'

class MonitoringPropertySerializer(serializers.ModelSerializer):
    ep_especie = SpecieForrestPropertySerializer()
    ep_usuario = PropertyUserSerializer()
    ep_predio = PropertySerializer()
    cant_monitoreos_r = serializers.IntegerField(read_only=True)
    diferencia_monitoreos = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserPropertyFile
        fields = '__all__'