import random, string
from django.db import IntegrityError
from rest_framework import serializers

from ..models import Users
from ..species.models import SpecieForrest
from ..candidates.models import CandidatesTrees
from .models import Monitorings, ViewMonitorings

class MonitoringTreesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitorings
        fields = ['id', 'evaluacion', 'fecha_monitoreo', 'user']

class CandidateTreesMonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidatesTrees
        fields = ['id', 'numero_placa', 'cod_expediente', 'cod_especie_id']

class UsersMonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'first_name', 'last_name']

class SpecieForrestMonSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecieForrest
        fields = ['id', 'habit', 'vernacularName', 'nombre_cientifico']

class MonitoringsSerializer(serializers.ModelSerializer):
    evaluacion = CandidateTreesMonSerializer()
    user = UsersMonSerializer()
    specie = SpecieForrestMonSerializer(source='evaluacion.cod_especie')

    class Meta:
        model = Monitorings
        fields = '__all__'

class MonitoringCreateSerializer(serializers.ModelSerializer):
    # Usa PrimaryKeyRelatedField para aceptar IDs directamente en lugar de objetos anidados
    evaluacion = serializers.PrimaryKeyRelatedField(queryset=CandidatesTrees.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())

    class Meta:
        model = Monitorings
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},  # El 'id' se generará automáticamente si no está en validated_data
        }

    def generate_random_id(self, length=8):
        """Genera un ID alfanumérico único."""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def create(self, validated_data):
        # Genera un 'id' alfanumérico único
        while True:
            random_id = self.generate_random_id()
            if not Monitorings.objects.filter(id=random_id).exists():
                break
        validated_data['id'] = random_id
        
        try:
            instance = super().create(validated_data)
            return instance
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                raise serializers.ValidationError({
                    'id': f"El id de monitoreo '{validated_data['id']}' ya está registrado en otro monitoreo."
                })
            else:
                raise e

class ViewMonitoringsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewMonitorings
        fields = '__all__'