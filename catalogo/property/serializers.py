from rest_framework import serializers
from .models import Property, UserPropertyFile, SpeciesRecord
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
        fields = ['id', 'vernacularName', 'scientificName', 'scientificNameAuthorship', 'habit']

class UserPropertyFileAllSerializer(serializers.ModelSerializer):
    ep_usuario = PropertyUserSerializer()
    ep_predio = PropertySerializer()

    class Meta:
        model = UserPropertyFile
        fields = '__all__'

class UserPropertyFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPropertyFile
        fields = '__all__'
    
class SpeciesRecordSerializer(serializers.ModelSerializer):
    ep_especie = SpecieForrestPropertySerializer()
    expediente = UserPropertyFileAllSerializer()
    
    class Meta:
        model = SpeciesRecord
        fields = '__all__'

class SpeciesRecordCreateSerializer(serializers.ModelSerializer):
    # Cambiamos el campo 'expediente' para que acepte el ID del expediente
    expediente = serializers.PrimaryKeyRelatedField(queryset=UserPropertyFile.objects.all())
    # El campo ep_especie se recibe como entero (code_specie)
    ep_especie = serializers.IntegerField(write_only=True)

    class Meta:
        model = SpeciesRecord
        fields = '__all__'

    def validate_ep_especie(self, value):
        try:
            # Validar si existe una especie con el code_specie proporcionado
            return SpecieForrest.objects.get(code_specie=value)
        except SpecieForrest.DoesNotExist:
            raise serializers.ValidationError("El código de especie proporcionado no es válido.")

    def create(self, validated_data):
        # Obtener la instancia de SpecieForrest usando el code_specie validado
        ep_especie_instance = validated_data.pop('ep_especie')
        validated_data['ep_especie'] = ep_especie_instance
        return super().create(validated_data)

class MonitoringPropertySerializer(serializers.ModelSerializer):
    ep_usuario = PropertyUserSerializer()
    ep_predio = PropertySerializer()
    cant_monitoreos_r = serializers.IntegerField(read_only=True)
    diferencia_monitoreos = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserPropertyFile
        fields = '__all__'