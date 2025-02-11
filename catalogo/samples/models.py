from django.conf import settings
from django.db import models
from ..models import Users
from ..candidates.models import CandidatesTrees

class Samples(models.Model):
    id = models.CharField(primary_key=True, max_length=60)
    evaluacion = models.ForeignKey(CandidatesTrees, on_delete=models.RESTRICT)
    fecha_coleccion = models.DateField(blank=True, null=True)
    nro_muestras = models.CharField(max_length=5, blank=True, null=True)
    user = models.ForeignKey(Users, on_delete=models.RESTRICT)
    siglas_colector_ppal = models.CharField(max_length=20, blank=True, null=True)
    nro_coleccion = models.IntegerField(blank=True, null=True)
    voucher = models.CharField(max_length=20, blank=True, null=True)
    nombres_colectores = models.TextField(blank=True, null=True)
    codigo_muestra = models.CharField(max_length=255, blank=True, null=True)
    otros_nombres = models.CharField(max_length=255, null=True)
    descripcion = models.TextField(blank=True, null=True)
    usos = models.TextField(blank=True, null=True)
    familia_especie = models.CharField(max_length=50, null=True)
    nombre_cientifico_muestra = models.CharField(max_length=100, blank=True, null=True)
    observacion = models.CharField(max_length=300, blank=True, null=True)
    verificado = models.CharField(max_length=15, blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'muestras_c'