# Generated by Django 4.2.1 on 2023-05-22 02:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EspecieForestal',
            fields=[
                ('ShortcutID', models.CharField(blank=True, max_length=60, null=True)),
                ('cod_especie', models.IntegerField(blank=True, null=True)),
                ('nom_comunes', models.CharField(blank=True, max_length=100, null=True)),
                ('otros_nombres', models.CharField(blank=True, max_length=250, null=True)),
                ('nombre_cientifico', models.CharField(blank=True, max_length=60, null=True)),
                ('sinonimos', models.TextField(blank=True, null=True)),
                ('familia', models.CharField(blank=True, max_length=60, null=True)),
                ('foto_general', models.CharField(blank=True, max_length=100, null=True)),
                ('distribucion', models.TextField(blank=True, null=True)),
                ('habito', models.CharField(blank=True, max_length=100, null=True)),
                ('follaje', models.CharField(blank=True, max_length=15, null=True)),
                ('forma_copa', models.CharField(blank=True, max_length=25, null=True)),
                ('tipo_hoja', models.CharField(blank=True, max_length=15, null=True)),
                ('disposicion_hojas', models.CharField(blank=True, max_length=30, null=True)),
                ('foto_hojas', models.CharField(blank=True, max_length=200, null=True)),
                ('hojas', models.TextField(blank=True, null=True)),
                ('foto_flor', models.CharField(blank=True, max_length=200, null=True)),
                ('flor', models.TextField(blank=True, null=True)),
                ('foto_fruto', models.CharField(blank=True, max_length=200, null=True)),
                ('frutos', models.TextField(blank=True, null=True)),
                ('foto_semillas', models.CharField(blank=True, max_length=200, null=True)),
                ('semillas', models.TextField(blank=True, null=True)),
                ('tallo', models.TextField(blank=True, null=True)),
                ('raiz', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'especie_forestal',
                'managed': False,
            },
        ),
    ]
