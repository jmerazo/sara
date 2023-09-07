from rest_framework import serializers
from .models import EspecieForestal, Glossary, CandidateTrees, Monitoring, Page, Users
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class EspecieForestalSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspecieForestal
        fields = '__all__'

class NombresComunesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspecieForestal
        fields = ['nom_comunes']

class FamiliaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspecieForestal
        fields = ['familia']

class NombreCientificoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspecieForestal
        fields = ['nombre_cientifico','nom_comunes', 'distribucion' ,'foto_general']

class GlossarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Glossary
        fields = '__all__'
        """ read_only_fields = ['id']

    def validate_word(self, value):
        # Ejemplo de validación personalizada para el campo 'word'
        if len(value) < 3:
            raise serializers.ValidationError("La palabra debe tener al menos 3 caracteres.")
        return value

    def to_representation(self, instance):
        # Ejemplo de personalización de la representación de datos
        representation = super().to_representation(instance)
        # Puedes manipular la representación antes de devolverla
        representation['word'] = representation['word'].upper()
        return representation """

class GeoCandidateTreesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateTrees
        fields = ['cod_especie', 'abcisa_xy']

class AverageTreesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateTrees
        fields = ['cod_especie', 'altitud', 'altura_total', 'altura_comercial', 'cobertura']

class TreesVerifyMonitoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateTrees
        fields = ['ShortcutIDEV', 'numero_placa', 'cod_especie', 'fecha_evaluacion', 'usuario_evaluador', 'departamento', 'municipio']

class CandidateTreesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateTrees
        fields = '__all__'

class MonitoringTreesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitoring
        fields = ['IDmonitoreo', 'ShortcutIDEV', 'fecha_monitoreo', 'usuario_realiza_monitoreo']

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'

class UsersSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Users  # o tu modelo de usuario personalizado
        fields = '__all__'

    def create(self, validated_data):
        # Hash de la contraseña antes de guardarla en la base de datos
        validated_data['password'] = make_password(validated_data['password'])
        return super(UsersSerializer, self).create(validated_data)