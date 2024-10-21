import random, string
from django.db import IntegrityError
from rest_framework import serializers

from .models import SpecieForrest, ImageSpeciesRelated, Families, SpeciesGBIF


class ImageSpeciesRelatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageSpeciesRelated
        fields = '__all__'

class SpecieForrestSerializer(serializers.ModelSerializer):
    images = ImageSpeciesRelatedSerializer(many=True, read_only=True)

    class Meta:
        model = SpecieForrest
        fields = '__all__'
        read_only_fields = ['id']

class SpecieForrestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecieForrest
        fields = '__all__'
        read_only_fields = ['id']

class SpecieForrestCreatSerializer(serializers.ModelSerializer):
    images = ImageSpeciesRelatedSerializer(many=True, read_only=True)
    class Meta:
        model = SpecieForrest
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},  # El 'id' se generará automáticamente
        }

    def create(self, validated_data):
        # Generamos un 'id' alfanumérico único
        while True:
            random_id = self.generate_random_id(8)
            if not SpecieForrest.objects.filter(id=random_id).exists():
                break
        validated_data['id'] = random_id
        try:
            instance = super().create(validated_data)
            return instance
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                raise serializers.ValidationError({
                    'code_specie': f"El código de especie '{validated_data['code_specie']}' ya está registrado en otra especie."
                })
            else:
                raise e  # Re-levantar la excepción si es otro tipo de IntegrityError

    @staticmethod
    def generate_random_id(length):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

# Return top species
class ImageSpeciesTopSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageSpeciesRelated
        fields = ['img_general']

class SpecieForrestTopSerializer(serializers.ModelSerializer):
    images = ImageSpeciesTopSerializer(many=True, read_only=True)

    class Meta:
        model = SpecieForrest
        fields = ['code_specie', 'vernacularName', 'images']

class NombresComunesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecieForrest
        fields = ['vernacularName']

class FamiliaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecieForrest
        fields = ['family']

class NombreCientificoSerializer(serializers.ModelSerializer):
    nombre_cientifico = serializers.SerializerMethodField()

    class Meta:
        model = SpecieForrest
        fields = ['code_specie', 'scientificName', 'scientificNameAuthorship', 'nombre_cientifico']

    def get_nombre_cientifico(self, obj):
        return f"{obj.nombre_cientifico_especie} {obj.nombre_autor_especie}"

class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Families
        fields = '__all__'

class SpeciesGBIFSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeciesGBIF
        fields = '__all__'
        read_only_fields = ['id']