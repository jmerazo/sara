from django.contrib import admin
from .models import EspecieForestal

class EspecieForestalAdmin(admin.ModelAdmin):
    pass
admin.site.register(EspecieForestal, EspecieForestalAdmin)