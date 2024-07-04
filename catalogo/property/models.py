from django.db import models
from ..species.models import specieForrest
from ..models import Users, Departments, Cities

class Property(models.Model):
    id = models.IntegerField(primary_key=True, null=True)
    p_user = models.ForeignKey(Users, on_delete=models.RESTRICT, null=True)
    nombre_predio = models.CharField(max_length=100, blank=True, null=True)
    p_departamento = models.ForeignKey(Departments, on_delete=models.RESTRICT)
    p_municipio = models.ForeignKey(Cities, on_delete=models.RESTRICT)

    class Meta:
        managed = False
        db_table = 'predios'

class UserPropertyFile(models.Model):
    id = models.IntegerField(primary_key=True, null=True)
    ep_especie_cod = models.IntegerField(null=True)
    ep_usuario = models.ForeignKey(Users, on_delete=models.RESTRICT)
    cantidad_individuos = models.IntegerField(blank=True, null=True)
    cant_productiva = models.IntegerField(blank=True, null=True)
    cant_remanente = models.IntegerField(blank=True, null=True)
    ep_predio = models.ForeignKey(Property, on_delete=models.RESTRICT)
    expediente = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario_expediente_predio'