from rest_framework import serializers
from .models import specieForrest, ImageSpeciesRelated, Families

class EspecieForestalSerializer(serializers.ModelSerializer):
    class Meta:
        model = specieForrest
        fields = '__all__'

class ImagesSpeciesRelatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageSpeciesRelated
        fields = '__all__'

class NombresComunesSerializer(serializers.ModelSerializer):
    class Meta:
        model = specieForrest
        fields = ['nom_comunes']

class FamiliaSerializer(serializers.ModelSerializer):
    class Meta:
        model = specieForrest
        fields = ['familia']

class NombreCientificoSerializer(serializers.ModelSerializer):
    nombre_cientifico = serializers.SerializerMethodField()

    class Meta:
        model = specieForrest
        fields = ['cod_especie', 'nombre_cientifico_especie', 'nombre_autor_especie', 'nombre_cientifico']

    def get_nombre_cientifico(self, obj):
        return f"{obj.nombre_cientifico_especie} {obj.nombre_autor_especie}"

class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Families
        fields = '__all__'