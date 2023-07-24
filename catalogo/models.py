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

class Glossary(models.Model):
    id = models.IntegerField(primary_key=True, blank=False)
    word = models.CharField(max_length=100)
    definition = models.TextField()

    class Meta:
        managed = False
        db_table = 'glossary'

    def __str__(self):
        return f"ID: {self.id}, Word: {self.word}, Definition: {self.definition}"
    
class CandidateTrees(models.Model):
    ShortcutIDEV = models.CharField(primary_key=True, max_length=60, blank=True)
    numero_placa = models.IntegerField(blank=True, null=True)
    cod_expediente = models.CharField(max_length=35, blank=True, null=True)
    cod_especie = models.CharField(max_length=50, blank=True, null=True)
    fecha_evaluacion = models.DateField()
    usuario_evaluador = models.CharField(max_length=50, blank=True, null=True)
    departamento = models.CharField(max_length=60, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    nombre_del_predio = models.CharField(max_length=60, blank=True, null=True)
    nombre_propietario = models.CharField(max_length=60, blank=True, null=True)
    corregimiento = models.CharField(max_length=60, blank=True, null=True)
    vereda = models.CharField(max_length=60, blank=True, null=True)
    correo = models.CharField(max_length=100, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    altitud = models.IntegerField()
    latitud = models.CharField(max_length=1, blank=True, null=True)
    g_lat = models.IntegerField()
    m_lat = models.IntegerField()
    s_lat = models.CharField(max_length=4, blank=True, null=True)
    longitud = models.CharField(max_length=1, blank=True, null=True)
    g_long = models.IntegerField()
    m_long = models.IntegerField()
    s_long = models.CharField(max_length=4, blank=True, null=True)
    coordenadas_decimales = models.CharField(max_length=150, blank=True, null=True)
    abcisa_xy = models.CharField(max_length=255, blank=True, null=True)
    altura_total = models.CharField(max_length=15, blank=True, null=True)
    altura_comercial = models.CharField(max_length=15, blank=True, null=True)
    cap = models.CharField(max_length=15, blank=True, null=True)
    cobertura = models.CharField(max_length=100, blank=True, null=True)
    cober_otro = models.CharField(max_length=30, blank=True, null=True)
    dominancia_if = models.CharField(max_length=16, blank=True,null=True)
    forma_fuste = models.CharField(max_length=40, blank=True, null=True)
    dominancia = models.CharField(max_length=70, blank=True, null=True)
    alt_bifurcacion = models.CharField(max_length=40, blank=True, null=True)
    estado_copa = models.CharField(max_length=30, blank=True, null=True)
    posicion_copa = models.CharField(max_length=40, blank=True, null=True)
    fitosanitario = models.CharField(max_length=40, blank=True, null=True)
    presencia = models.CharField(max_length=70, blank=True, null=True)
    resultado = models.IntegerField()
    evaluacion = models.CharField(max_length=145, blank=True, null=True)
    observaciones = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'evaluacion_as'

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