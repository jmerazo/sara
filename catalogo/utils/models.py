from django.db import models

class Rol(models.Model):
    name = models.CharField(max_length=35, blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'roles'

class Glossary(models.Model):
    id = models.IntegerField(primary_key=True)
    word = models.CharField(max_length=100)
    definition = models.TextField()

    class Meta:
        managed = False
        db_table = 'glossary'

    def __str__(self):
        return f"ID: {self.id}, Word: {self.word}, Definition: {self.definition}"
    
class Sisa(models.Model):
    codigo = models.IntegerField(null=True, blank=True)
    nombres_comunes = models.CharField(max_length=255, null=True, blank=True)
    nombre_cientifico = models.CharField(max_length=200, null=True, blank=True)
    nom_cient_res = models.CharField(max_length=200, blank=True, null=True)
    flia_apg = models.CharField(max_length=60, blank=True, null=True)
    flia_cronquist = models.CharField(max_length=60, blank=True, null=True)
    clasificacion_res = models.CharField(max_length=60, blank=True, null=True)    

    class Meta:
        managed = False
        db_table = 'species_sisa'