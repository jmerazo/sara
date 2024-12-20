from django.db import models
from ..models import Users, Departments, Cities
from ..species.models import SpecieForrest

class Property(models.Model):
    p_user = models.ForeignKey(Users, on_delete=models.RESTRICT, null=True)
    nombre_predio = models.CharField(max_length=100, blank=True, null=True)
    p_departamento = models.ForeignKey(Departments, on_delete=models.RESTRICT)
    p_municipio = models.ForeignKey(Cities, on_delete=models.RESTRICT)
    corregimiento = models.CharField(max_length=80, blank=True, null=True)
    vereda = models.CharField(max_length=80, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'predios'

class UserPropertyFile(models.Model):
    expediente = models.CharField(max_length=50, blank=True, null=True)
    resolucion = models.CharField(max_length=50, blank=True, null=True)
    fecha_exp = models.DateField()
    ep_usuario = models.ForeignKey(Users, on_delete=models.RESTRICT)
    ep_predio = models.ForeignKey(Property, on_delete=models.RESTRICT)
    ep_especie = models.ForeignKey(SpecieForrest, to_field='code_specie', on_delete=models.RESTRICT)  # Relación basada en code_specie
    tamano_UMF = models.IntegerField(blank=True, null=True)
    cantidad_autorizada = models.IntegerField(blank=True, null=True)
    cantidad_remanentes = models.IntegerField(blank=True, null=True)
    cantidad_aprovechable = models.IntegerField(blank=True, null=True)
    cant_monitoreos = models.IntegerField(blank=True, null=True)
    PCM = models.IntegerField(blank=True, null=True)
    PRM = models.IntegerField(blank=True, null=True)
    cantidad_placas = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario_expediente_predio'