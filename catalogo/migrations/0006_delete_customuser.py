# Generated by Django 4.1.1 on 2023-09-29 17:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0005_customuser_delete_userprofile'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]