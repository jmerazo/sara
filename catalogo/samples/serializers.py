from rest_framework import serializers
from .models import Samples
from ..models import Users
from ..candidates.models import CandidatesTrees
from ..species.models import SpecieForrest

class UserSamplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'first_name', 'last_name']

class CandidatesSamplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidatesTrees
        fields = ['id', 'numero_placa', 'cod_expediente', 'cod_especie_id']

class SpecieForrestMonSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecieForrest
        fields = ['id', 'habit', 'vernacularName', 'nombre_cientifico']

class SamplesSerializer(serializers.ModelSerializer):
    user = UserSamplesSerializer()
    evaluacion = CandidatesSamplesSerializer()
    specie = SpecieForrestMonSerializer(source='evaluacion.cod_especie')

    class Meta:
        model = Samples
        fields = '__all__'

class SamplesCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())
    evaluacion = serializers.PrimaryKeyRelatedField(queryset=CandidatesTrees.objects.all())

    class Meta:
        model = Samples
        fields = '__all__'