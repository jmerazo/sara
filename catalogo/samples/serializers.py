from rest_framework import serializers
from .models import Samples
from ..models import Users
from ..users.serializers import UsersSerializer
from ..candidates.models import CandidatesTrees
from ..candidates.serializers import CandidateTreesSerializer

class SamplesSerializer(serializers.ModelSerializer):
    user = UsersSerializer()
    evaluacion = CandidateTreesSerializer()

    class Meta:
        model = Samples
        fields = '__all__'

class SamplesCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())
    evaluacion = serializers.PrimaryKeyRelatedField(queryset=CandidatesTrees.objects.all())

    class Meta:
        model = Samples
        fields = '__all__'