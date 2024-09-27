from rest_framework import serializers
from .models import Monitorings, ViewMonitorings
from ..candidates.models import CandidatesTrees
from ..models import Users
from ..candidates.serializers import CandidateTreesSerializer
from ..users.serializers import UsersSerializer
from ..species.models import SpecieForrest
from ..species.serializers import SpecieForrestSerializer

class MonitoringTreesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitorings
        fields = ['id', 'evaluacion', 'fecha_monitoreo', 'usuario_realiza_monitoreo']

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

class ViewMonitoringsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewMonitorings
        fields = '__all__'