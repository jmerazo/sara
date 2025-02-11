from django.db import models
from django.contrib.auth.models import BaseUserManager
from ..page.models import Pages

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
    
class UserModules(models.Model):
    id = models.AutoField(primary_key=True)
    rol_id = models.IntegerField()
    page = models.ForeignKey(Pages, on_delete=models.RESTRICT)
    add = models.SmallIntegerField()
    update = models.SmallIntegerField()
    delete = models.SmallIntegerField()
    download = models.SmallIntegerField()
    view_ubication = models.SmallIntegerField()
    info_colectors = models.SmallIntegerField()
    view_candidates = models.SmallIntegerField()
    view_monitoring = models.SmallIntegerField()

    class Meta:
        db_table = 'users_modules'