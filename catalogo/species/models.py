from django.db import models

class SpecieForrest(models.Model):
    id = models.CharField(primary_key=True, max_length=60) # identificador
    code_specie = models.IntegerField(unique=True) # código especie
    vernacularName = models.CharField(max_length=100, blank=True, null=True) # nombre común
    otherNames = models.CharField(max_length=250, blank=True, null=True) # otros nombres
    nombre_cientifico = models.CharField(max_length=150, blank=True, null=True) 
    scientificName = models.CharField(max_length=150, blank=True, null=True) # nombre cientifico
    scientificNameAuthorship = models.CharField(max_length=150, blank=True, null=True) # nombre autor
    kingdom = models.CharField(max_length=50, blank=True, null=True) # reino
    phylum = models.CharField(max_length=50, blank=True, null=True) # filo
    clas = models.CharField(max_length=50, blank=True, null=True, db_column='class') # clase
    order = models.CharField(max_length=50, blank=True, null=True) # orden
    synonyms = models.TextField(blank=True, null=True) # sinonimos
    family = models.CharField(max_length=60, blank=True, null=True) # familia
    genus = models.CharField(max_length=50, blank=True, null=True) # genero
    distribution = models.TextField(blank=True, null=True) # distribución
    descriptionGeneral = models.TextField(blank=True, null=True) # descripción general
    habit = models.CharField(max_length=30, blank=True, null=True) # habito
    leaves = models.TextField(blank=True, null=True) # hojas
    flowers = models.TextField(blank=True, null=True) # flores
    fruits = models.TextField(blank=True, null=True) # frutos
    seeds = models.TextField(blank=True, null=True) # semillas
    woodUses = models.TextField(blank=True, null=True) # usos maderables
    nonTimberUsers = models.TextField(blank=True, null=True) # usos no maderables
    bloom = models.TextField(blank=True, null=True) # floración
    fructification = models.TextField(blank=True, null=True) # fructificación
    ecology = models.TextField(blank=True, null=True) # ecologia
    specificEpithet = models.CharField(max_length=100, blank=True, null=True) # epíteto específico
    infraspecificEpithet = models.CharField(max_length=100, blank=True, null=True) # epíteto infragenérico
    taxonRank = models.CharField(max_length=50, blank=True, null=True) # categoría del taxón
    taxon_key = models.IntegerField(blank=True, null=True) # id gbif
    views = models.IntegerField(blank=True, null=True) # vistas

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