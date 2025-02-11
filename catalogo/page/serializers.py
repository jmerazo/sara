from rest_framework import serializers
from .models import Page, Pages, Section, SliderImages

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'

class PagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pages
        fields = '__all__'

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'

class SliderImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SliderImages
        fields = '__all__'