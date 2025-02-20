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
    clase_vivero = models.CharField(max_length=100, blank=True, null=True)
    vigencia_registro = models.SmallIntegerField(max_length=1, blank=True, null=True)
    tipo_registro = models.CharField(max_length=100, blank=True, null=True)
    numero_registro_ica = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'viveros'

class UserNurseries(models.Model):
    id = models.AutoField(primary_key=True)
    vivero = models.ForeignKey(Nurseries, on_delete=models.RESTRICT, null=True)
    especie_forestal = models.ForeignKey(SpecieForrest, to_field='code_specie', on_delete=models.RESTRICT, db_column='especie_forestal_id')
    tipo_venta = models.CharField(max_length=100, blank=True, null=True)
    unidad_medida = models.CharField(max_length=50, blank=True, null=True)
    cantidad_stock = models.IntegerField(blank=True, null=True)
    ventas_realizadas = models.IntegerField(blank=True, null=True)
    total_disponible = models.IntegerField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    activo = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'userespecieforestal'
