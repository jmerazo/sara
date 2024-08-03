from rest_framework import serializers
from .models import Monitorings
from ..candidates.serializers import CandidateTreesSerializer
from ..users.serializers import UsersSerializer

class MonitoringTreesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitorings
        fields = ['id', 'evaluacion', 'fecha_monitoreo', 'usuario_realiza_monitoreo']

class MonitoringsSerializer(serializers.ModelSerializer):
    evaluacion = CandidateTreesSerializer()
    user = UsersSerializer()

    class Meta:
        model = Monitorings
        fields = '__all__'