from django.db import models

class specieForrest(models.Model):
    ShortcutID = models.CharField(primary_key=True, max_length=60, blank=True)  # Field name made lowercase.
    cod_especie = models.IntegerField(blank=True, null=True)
    nom_comunes = models.CharField(max_length=100, blank=True, null=True)
    otros_nombres = models.CharField(max_length=250, blank=True, null=True)
    nombre_cientifico = models.CharField(max_length=150, blank=True, null=True)
    nombre_cientifico_especie = models.CharField(max_length=150, blank=True, null=True)
    nombre_autor_especie = models.CharField(max_length=150, blank=True, null=True)
    sinonimos = models.TextField(blank=True, null=True)
    familia = models.CharField(max_length=60, blank=True, null=True)
    distribucion = models.TextField(blank=True, null=True)
    descripcion_general = models.TextField(blank=True, null=True)
    hojas = models.TextField(blank=True, null=True)
    flor = models.TextField(blank=True, null=True)
    frutos = models.TextField(blank=True, null=True)
    semillas = models.TextField(blank=True, null=True)
    usos_maderables = models.TextField(blank=True, null=True)
    usos_no_maderables = models.TextField(blank=True, null=True)
    taxon_key = models.IntegerField(blank=True, null=True)
    visitas = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'especie_forestal'

    def __str__(self):
        return f"Nombre común: {self.nom_comunes}, Nombre científico: {self.nombre_cientifico_especie},Código de especie: {self.cod_especie}"

class ImageSpeciesRelated(models.Model):
    id = models.IntegerField(primary_key=True)
    specie_id = models.CharField(max_length=10, blank=True, null=True)
    img_general = models.CharField(max_length=150, blank=True, null=True)
    img_leafs = models.CharField(max_length=150, blank=True, null=True)
    img_fruits = models.CharField(max_length=150, blank=True, null=True)
    img_flowers = models.CharField(max_length=150, blank=True, null=True)
    img_seeds = models.CharField(max_length=150, blank=True, null=True)
    img_stem = models.CharField(max_length=150, blank=True, null=True)
    img_landscape_one = models.CharField(max_length=150, blank=True, null=True)
    img_landscape_two = models.CharField(max_length=150, blank=True, null=True)
    img_landscape_three = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'img_species'

class Families(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=False)
    description = models.TextField(blank=True, null=True)
    active = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'families'