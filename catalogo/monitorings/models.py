from django.db import models

class Monitorings(models.Model):
    IDmonitoreo = models.CharField(primary_key=True, max_length=50)  # Field name made lowercase.
    ShortcutIDEV = models.CharField(max_length=50)  # Field name made lowercase.
    fecha_monitoreo = models.DateField(blank=True, null=True)
    hora = models.TimeField(blank=True, null=True)
    usuario_realiza_monitoreo = models.CharField(db_column='Usuario quien realiza el monitoreo', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    temperatura = models.CharField(max_length=10, blank=True, null=True)
    humedad = models.CharField(max_length=10, blank=True, null=True)
    precipitacion = models.CharField(max_length=13, blank=True, null=True)
    factor_climatico = models.CharField(max_length=20, blank=True, null=True)
    observaciones_temp = models.CharField(max_length=255, blank=True, null=True)
    cap = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    altura_total = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    altura_del_fuste = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    eje_x = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    eje_y = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    eje_z = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    fitosanitario = models.CharField(max_length=7, blank=True, null=True)
    afectacion = models.CharField(max_length=500, blank=True, null=True)
    observaciones_afec = models.CharField(max_length=200, blank=True, null=True)
    follaje = models.CharField(max_length=50, blank=True, null=True)
    follaje_porcentaje = models.CharField(max_length=50, blank=True, null=True)
    observaciones_follaje = models.CharField(max_length=255, blank=True, null=True)
    flor_abierta = models.CharField(max_length=15, blank=True, null=True)
    flor_boton = models.CharField(max_length=15, blank=True, null=True)
    color_flor = models.CharField(max_length=20, blank=True, null=True)
    color_flor_otro = models.CharField(max_length=50, blank=True, null=True)
    olor_flor = models.CharField(max_length=30, blank=True, null=True)
    olor_flor_otro = models.CharField(max_length=50, blank=True, null=True)
    fauna_flor = models.CharField(max_length=30, blank=True, null=True)
    fauna_flor_otros = models.CharField(max_length=50, blank=True, null=True)
    observaciones_flor = models.CharField(max_length=200, blank=True, null=True)
    frutos_verdes = models.CharField(max_length=15, blank=True, null=True)
    estado_madurez = models.CharField(max_length=15, blank=True, null=True)
    color_fruto = models.CharField(max_length=20, blank=True, null=True)
    color_fruto_otro = models.CharField(max_length=50, blank=True, null=True)
    medida_peso_frutos = models.CharField(max_length=30, blank=True, null=True)
    peso_frutos = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True)
    fauna_frutos = models.CharField(max_length=30, blank=True, null=True)
    fauna_frutos_otro = models.CharField(max_length=50, blank=True, null=True)
    observacion_frutos = models.CharField(max_length=200, blank=True, null=True)
    medida_peso_sem = models.CharField(max_length=30, blank=True, null=True)
    peso_semillas = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    observacion_semilla = models.CharField(max_length=200, blank=True, null=True)
    entorno = models.CharField(max_length=51, blank=True, null=True)
    entorno_otro = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'monitoreo'