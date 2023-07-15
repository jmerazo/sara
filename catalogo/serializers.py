from rest_framework import serializers
from .models import EspecieForestal, Glossary

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
        fields = ['id', 'word', 'definition']
        read_only_fields = ['id']

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
        return representation