from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, Group, Permission
from django.utils import timezone

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

class Users(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    rol = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(max_length=30, blank=True, null=True, default=False)
    document_type = models.CharField(max_length=40, blank=True, null=True)
    document_number = models.CharField(max_length=20, blank=True, null=True)
    entity = models.CharField(max_length=100, blank=True, null=True)
    cellphone = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=25, blank=True, null=True)
    city = models.IntegerField(blank=True, null=True)
    device_movile = models.CharField(max_length=2, blank=True, null=True)
    serial_device = models.CharField(max_length=17, blank=True, null=True)
    profession = models.CharField(max_length=150, blank=True, null=True)
    reason = models.CharField(max_length=500, blank=True, null=True)
    state = models.CharField(max_length=25, blank=True, null=True, default='REVIEW')
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(default=timezone.now)
    is_superuser = models.SmallIntegerField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    groups = models.ManyToManyField(Group, blank=True)
    user_permissions = models.ManyToManyField(Permission, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        managed = True
        db_table = 'Users'

    def __str__(self):
        return self.email


class Glossary(models.Model):
    id = models.IntegerField(primary_key=True, blank=False)
    word = models.CharField(max_length=100)
    definition = models.TextField()

    class Meta:
        managed = False
        db_table = 'glossary'

    def __str__(self):
        return f"ID: {self.id}, Word: {self.word}, Definition: {self.definition}"
    

class Departments(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'departments'

class Cities(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=60, blank=True, null=True)
    department_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'cities'