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
    
class PropertyCreateSerializer(serializers.ModelSerializer):
    # Aceptar únicamente IDs
    p_user = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all(), required=True)
    p_departamento = serializers.PrimaryKeyRelatedField(queryset=DepartmentsSerializer.Meta.model.objects.all(), required=True)
    p_municipio = serializers.PrimaryKeyRelatedField(queryset=CitiesSerializer.Meta.model.objects.all(), required=True)

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
    ep_especie = serializers.IntegerField(write_only=True)  # Aceptar code_specie como entero
    ep_especie_detail = SpecieForrestPropertySerializer(read_only=True, source='ep_especie')  # Serializador para mostrar detalles

    class Meta:
        model = UserPropertyFile
        fields = '__all__'

    def validate_ep_especie(self, value):
        try:
            # Validar si existe una especie con el code_specie proporcionado
            return SpecieForrest.objects.get(code_specie=value)
        except SpecieForrest.DoesNotExist:
            raise serializers.ValidationError("El código de especie proporcionado no es válido.")

    def create(self, validated_data):
        # Asignar instancia de SpecieForrest al campo ep_especie
        validated_data['ep_especie'] = validated_data.pop('ep_especie')
        return super().create(validated_data)

class MonitoringPropertySerializer(serializers.ModelSerializer):
    ep_especie = SpecieForrestPropertySerializer()
    ep_usuario = PropertyUserSerializer()
    ep_predio = PropertySerializer()
    cant_monitoreos_r = serializers.IntegerField(read_only=True)
    diferencia_monitoreos = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserPropertyFile
        fields = '__all__'