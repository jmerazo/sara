from django.db import models

class SpecieForrest(models.Model):
    id = models.CharField(primary_key=True, max_length=60)
    cod_especie = models.IntegerField(unique=True)
    nom_comunes = models.CharField(max_length=100, blank=True, null=True) # DELETE
    vernacularName = models.CharField(max_length=100, blank=True, null=True)
    otros_nombres = models.CharField(max_length=250, blank=True, null=True)
    nombre_cientifico = models.CharField(max_length=150, blank=True, null=True)
    nombre_cientifico_especie = models.CharField(max_length=150, blank=True, null=True) # DELETE
    scientificName = models.CharField(max_length=150, blank=True, null=True)
    nombre_autor_especie = models.CharField(max_length=150, blank=True, null=True)
    scientificNameAuthorship = models.CharField(max_length=150, blank=True, null=True)
    kingdom = models.CharField(max_length=50, blank=True, null=True)
    phylum = models.CharField(max_length=50, blank=True, null=True)
    clas = models.CharField(max_length=50, blank=True, null=True, db_column='class')
    order = models.CharField(max_length=50, blank=True, null=True)
    sinonimos = models.TextField(blank=True, null=True)
    familia = models.CharField(max_length=60, blank=True, null=True)
    family = models.CharField(max_length=60, blank=True, null=True)
    genus = models.CharField(max_length=50, blank=True, null=True)
    distribucion = models.TextField(blank=True, null=True)
    descripcion_general = models.TextField(blank=True, null=True)
    habitos = models.CharField(max_length=30, blank=True, null=True)
    hojas = models.TextField(blank=True, null=True)
    flor = models.TextField(blank=True, null=True)
    frutos = models.TextField(blank=True, null=True)
    semillas = models.TextField(blank=True, null=True)
    usos_maderables = models.TextField(blank=True, null=True)
    usos_no_maderables = models.TextField(blank=True, null=True)
    floracion = models.TextField(blank=True, null=True)
    fructificacion = models.TextField(blank=True, null=True)
    ecologia = models.TextField(blank=True, null=True)
    specificEpithet = models.CharField(max_length=100, blank=True, null=True)
    infraspecificEpithet = models.CharField(max_length=100, blank=True, null=True)
    taxonRank = models.CharField(max_length=50, blank=True, null=True)
    taxon_key = models.IntegerField(blank=True, null=True)
    views = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'especie_forestal_c'

class ImageSpeciesRelated(models.Model):
    specie = models.ForeignKey(SpecieForrest, on_delete=models.RESTRICT, related_name='images')
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