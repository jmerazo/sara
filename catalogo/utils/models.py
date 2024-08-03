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
    