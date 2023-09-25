from django.contrib import admin
from .models import EspecieForestal, Users

class EspecieForestalAdmin(admin.ModelAdmin):
    pass
admin.site.register(Users)