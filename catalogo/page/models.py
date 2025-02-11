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
        db_table = 'page'

class Pages(models.Model):
    router = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=150, blank=True, null=True)
    icon = models.CharField(max_length=250, blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'pages'

class Section(models.Model):
    page_id = models.IntegerField(blank=False, null=False)
    section_title = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=254, blank=True, null=True)
    content_type = models.CharField(max_length=254, blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    styles = models.JSONField(default=dict)

    class Meta:
        db_table = 'section'

class SliderImages(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    order = models.IntegerField(null=False, blank=False)
    status = models.SmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'slider_images'
