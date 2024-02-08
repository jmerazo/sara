from rest_framework import serializers
from .models import CandidatesTrees

class GeoCandidateTreesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidatesTrees
        fields = ['cod_especie', 'numero_placa','abcisa_xy', 'vereda', 'nombre_del_predio', 'resultado']

class AverageTreesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidatesTrees
        fields = ['cod_especie', 'altitud', 'altura_total', 'altura_fuste', 'cobertura']

class TreesVerifyMonitoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidatesTrees
        fields = ['ShortcutIDEV', 'numero_placa', 'cod_especie', 'fecha_evaluacion', 'usuario_evaluador', 'departamento', 'municipio']

# RETORNA DATOS DE LA TABLA EVALUACION_AS -> CORRESPONDE A CANDIDATOS
class CandidateTreesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidatesTrees
        fields = '__all__'