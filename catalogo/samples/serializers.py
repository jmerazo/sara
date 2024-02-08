from rest_framework import serializers
from .models import Samplez

class SamplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Samplez
        fields = '__all__'