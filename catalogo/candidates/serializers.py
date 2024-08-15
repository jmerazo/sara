from rest_framework import serializers
from .models import CandidatesTrees
from ..species.models import SpecieForrest
from ..species.serializers import SpecieForrestSerializer
from ..property.models import Property
from ..property.serializers import PropertySerializer
from ..models import Users
from ..users.serializers import UsersSerializer

# RETORNA DATOS DE LA TABLA EVALUACION_AS -> CORRESPONDE A CANDIDATOS
class SpecieForrestLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecieForrest
        fields = ['vernacularName', 'code_specie', 'scientificName', 'scientificNameAuthorship', 'habit']

class PropertyLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['nombre_predio', 'id']

class UsersLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'first_name', 'last_name']

class CandidateTreesSerializer(serializers.ModelSerializer):
    cod_especie = SpecieForrestLiteSerializer()
    user = UsersLiteSerializer()
    property = PropertyLiteSerializer()

    class Meta:
        model = CandidatesTrees
        fields = '__all__'

class CandidateTreesCreateSerializer(serializers.ModelSerializer):
    cod_especie = serializers.PrimaryKeyRelatedField(queryset=SpecieForrest.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())

    class Meta:
        model = CandidatesTrees
        fields = '__all__'

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