from rest_framework import serializers
from .models import Rol, Glossary, Sisa

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'

class GlossarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Glossary
        fields = '__all__'

class SisaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sisa
        fields = '__all__'
