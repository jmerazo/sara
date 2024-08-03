from django.db import models
from ..species.models import SpecieForrest
from ..models import Users
from ..models import Users, Departments, Cities

class Nurseries(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_vivero = models.CharField(max_length=100, blank=True, null=True)
    nit = models.CharField(max_length=20, blank=True, null=True)
    representante_legal = models.ForeignKey(Users, on_delete=models.RESTRICT)
    ubicacion = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    department = models.ForeignKey(Departments, on_delete=models.RESTRICT)
    city = models.ForeignKey(Cities, on_delete=models.RESTRICT)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    logo = models.CharField(max_length=255, blank=True, null=True)
    active = models.SmallIntegerField(default=1, null=True)

    class Meta:
        managed = False
        db_table = 'viveros'

class UserNurseries(models.Model):
    id = models.AutoField(primary_key=True)
    vivero = models.ForeignKey(Nurseries, on_delete=models.RESTRICT, null=True)
    especie_forestal = models.ForeignKey(SpecieForrest, to_field='cod_especie', on_delete=models.RESTRICT)
    tipo_venta = models.CharField(max_length=100, blank=True, null=True)
    unidad_medida = models.CharField(max_length=50, blank=True, null=True)
    cantidad_stock = models.IntegerField()
    ventas_realizadas = models.IntegerField()
    observaciones = models.TextField()
    activo = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'UserEspecieForestal'