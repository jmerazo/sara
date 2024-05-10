from rest_framework import serializers
from .models import Nurseries, UserNurseries
from ..serializers import UserSerializer
from ..species.serializers import NombreCientificoSerializer

class NurseriesSerializer(serializers.ModelSerializer):
    representante_legal = UserSerializer(read_only=True)

    class Meta:
        model = Nurseries
        fields = ['id', 'nombre_vivero', 'nit', 'representante_legal', 'ubicacion', 'email', 'telefono', 'department', 'city', 'direccion', 'logo', 'active']

class UserNurseriesSerializer(serializers.ModelSerializer):
    vivero = NurseriesSerializer(read_only=True)
    especie_forestal = NombreCientificoSerializer(read_only=True)

    class Meta:
        model = UserNurseries
        fields = ['id', 'vivero', 'especie_forestal', 'tipo_venta', 'unidad_medida', 'cantidad_stock', 'ventas_realizadas', 'observaciones', 'activo']