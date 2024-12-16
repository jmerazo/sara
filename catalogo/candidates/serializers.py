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
    cod_especie = serializers.SlugRelatedField(
        queryset=SpecieForrest.objects.all(),
        slug_field='code_specie',
        required=False  # Hace que este campo no sea obligatorio
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=Users.objects.all(),
        required=False  # Hace que este campo no sea obligatorio
    )
    property = serializers.PrimaryKeyRelatedField(
        queryset=Property.objects.all(),
        required=False  # Hace que este campo no sea obligatorio
    )

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

class CandidatesSpecieForrestSerializer(serializers.ModelSerializer):
    # Asumiendo que 'property' es un ForeignKey, no uses many=True
    property = PropertySerializer(read_only=True)
    specie = SpecieForrestLiteSerializer(source='cod_especie', read_only=True)

    class Meta:
        model = CandidatesTrees  # Asegúrate de que este es el modelo correcto
        fields = [
            'id', 
            'eventDate', 
            'numero_placa', 
            'cod_expediente', 
            'cod_especie_id', 
            'specie',
            'minimumElevationInMeters', 
            'cobertura', 
            'entorno_individuo', 
            'dominancia_if', 
            'forma_fuste', 
            'dominancia',
            'alt_bifurcacion',
            'estado_copa',
            'posicion_copa',
            'fitosanitario',
            'presencia',
            'resultado',
            'evaluacion',
            'observaciones',
            'property'
        ]
        read_only_fields = ['id']