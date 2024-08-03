from rest_framework import serializers
from .models import SpecieForrest, ImageSpeciesRelated, Families

class ImageSpeciesRelatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageSpeciesRelated
        fields = '__all__'

class SpecieForrestSerializer(serializers.ModelSerializer):
    images = ImageSpeciesRelatedSerializer(many=True, read_only=True)

    class Meta:
        model = SpecieForrest
        fields = '__all__'

# Return top species
class ImageSpeciesTopSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageSpeciesRelated
        fields = ['img_general']

class SpecieForrestTopSerializer(serializers.ModelSerializer):
    images = ImageSpeciesTopSerializer(many=True, read_only=True)

    class Meta:
        model = SpecieForrest
        fields = ['cod_especie', 'nom_comunes', 'images']

class NombresComunesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecieForrest
        fields = ['nom_comunes']

class FamiliaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecieForrest
        fields = ['familia']

class NombreCientificoSerializer(serializers.ModelSerializer):
    nombre_cientifico = serializers.SerializerMethodField()

    class Meta:
        model = SpecieForrest
        fields = ['cod_especie', 'nombre_cientifico_especie', 'nombre_autor_especie', 'nombre_cientifico']

    def get_nombre_cientifico(self, obj):
        return f"{obj.nombre_cientifico_especie} {obj.nombre_autor_especie}"

class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Families
        fields = '__all__'