from rest_framework import serializers
from .models import Monitorings

class MonitoringTreesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitorings
        fields = ['IDmonitoreo', 'ShortcutIDEV', 'fecha_monitoreo', 'usuario_realiza_monitoreo']

class MonitoringsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitorings
        fields = '__all__'