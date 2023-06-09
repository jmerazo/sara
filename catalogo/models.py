from django.db import models
from django.contrib.auth.models import User

class EspecieForestal(models.Model):
    ShortcutID = models.CharField(primary_key=True, max_length=60, blank=True)  # Field name made lowercase.
    cod_especie = models.IntegerField(blank=True, null=True)
    nom_comunes = models.CharField(max_length=100, blank=True, null=True)
    otros_nombres = models.CharField(max_length=250, blank=True, null=True)
    nombre_cientifico = models.CharField(max_length=60, blank=True, null=True)
    sinonimos = models.TextField(blank=True, null=True)
    familia = models.CharField(max_length=60, blank=True, null=True)
    foto_general = models.CharField(max_length=100, blank=True, null=True)
    distribucion = models.TextField(blank=True, null=True)
    habito = models.CharField(max_length=100, blank=True, null=True)
    follaje = models.CharField(max_length=15, blank=True, null=True)
    forma_copa = models.CharField(max_length=25, blank=True, null=True)
    tipo_hoja = models.CharField(max_length=15, blank=True, null=True)
    disposicion_hojas = models.CharField(max_length=30, blank=True, null=True)
    foto_hojas = models.CharField(max_length=200, blank=True, null=True)
    hojas = models.TextField(blank=True, null=True)
    foto_flor = models.CharField(max_length=200, blank=True, null=True)
    flor = models.TextField(blank=True, null=True)
    foto_fruto = models.CharField(max_length=200, blank=True, null=True)
    frutos = models.TextField(blank=True, null=True)
    foto_semillas = models.CharField(max_length=200, blank=True, null=True)
    semillas = models.TextField(blank=True, null=True)
    tallo = models.TextField(blank=True, null=True)
    raiz = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'especie_forestal'

    def __str__(self):
        return f"Nombre común: {self.nom_comunes}, Nombre científico: {self.nombre_cientifico} ,Código de especie: {self.cod_especie}"

"""
CharField: Campo de texto de longitud variable.
TextField: Campo de texto de longitud variable (para textos más largos).
IntegerField: Campo para números enteros.
FloatField: Campo para números de punto flotante.
BooleanField: Campo para valores booleanos (verdadero o falso).
DateField: Campo para almacenar fechas.
DateTimeField: Campo para almacenar fechas y horas.
TimeField: Campo para almacenar horas.
EmailField: Campo para almacenar direcciones de correo electrónico.
URLField: Campo para almacenar URLs.
FileField: Campo para cargar y almacenar archivos.
ImageField: Campo para cargar y almacenar imágenes.
ForeignKey: Campo para representar una relación de clave externa a otro modelo.
ManyToManyField: Campo para representar una relación de muchos a muchos con otros modelos.
"""