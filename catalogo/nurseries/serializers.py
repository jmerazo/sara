from rest_framework import serializers
from .models import Nurseries, UserNurseries
from ..serializers import UserSerializer
from ..species.models import SpecieForrest
from ..models import Users
from ..serializers import DepartmentsSerializer, CitiesSerializer

class NurserieUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'first_name', 'last_name']

class NurseriesSerializer(serializers.ModelSerializer):
    representante_legal = NurserieUserSerializer(read_only=True)
    department = DepartmentsSerializer()
    city = CitiesSerializer()

    class Meta:
        model = Nurseries
        fields = '__all__'

class SpecieForrestNurserieSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecieForrest
        fields = ['id', 'code_specie', 'vernacularName', 'scientificName', 'scientificNameAuthorship']

class UserNurseriesSerializer(serializers.ModelSerializer):
    vivero = NurseriesSerializer()
    especie_forestal = SpecieForrestNurserieSerializer()

    class Meta:
        model = UserNurseries
        fields = '__all__'

class UsersNurseriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNurseries
        fields = '__all__'