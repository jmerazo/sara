from rest_framework import serializers
from .models import EmpiricalKnowledge


# RETORNA DATOS DE LA TABLA EVALUACION_AS -> CORRESPONDE A CANDIDATOS
class EmpiricalKnowledgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpiricalKnowledge
        fields = '__all__'