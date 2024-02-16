from django.db import models

class Page(models.Model):
    id = models.IntegerField(primary_key=True)
    section = models.CharField(max_length=50, blank=True, null=True)
    router = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=300, blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'page'