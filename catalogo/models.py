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
    id = models.CharField(primary_key=True, max_length=50)
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

class EspecieForestal(models.Model):
    ShortcutID = models.CharField(primary_key=True, max_length=60, blank=True)  # Field name made lowercase.
    cod_especie = models.IntegerField(blank=True, null=True)
    nom_comunes = models.CharField(max_length=100, blank=True, null=True)
    otros_nombres = models.CharField(max_length=250, blank=True, null=True)
    nombre_cientifico = models.CharField(max_length=60, blank=True, null=True)
    sinonimos = models.TextField(blank=True, null=True)
    familia = models.CharField(max_length=60, blank=True, null=True)
    foto_general = models.CharField(max_length=100, blank=True, null=True)
    distribucion = models.TextField(blank=True, null=True)
    habito = models.CharField(max_length=100, blank=True, null=True)
    follaje = models.CharField(max_length=15, blank=True, null=True)
    forma_copa = models.CharField(max_length=25, blank=True, null=True)
    tipo_hoja = models.CharField(max_length=15, blank=True, null=True)
    disposicion_hojas = models.CharField(max_length=30, blank=True, null=True)
    foto_hojas = models.CharField(max_length=200, blank=True, null=True)
    hojas = models.TextField(blank=True, null=True)
    foto_flor = models.CharField(max_length=200, blank=True, null=True)
    flor = models.TextField(blank=True, null=True)
    foto_fruto = models.CharField(max_length=200, blank=True, null=True)
    frutos = models.TextField(blank=True, null=True)
    foto_semillas = models.CharField(max_length=200, blank=True, null=True)
    semillas = models.TextField(blank=True, null=True)
    tallo = models.TextField(blank=True, null=True)
    raiz = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'especie_forestal'

    def __str__(self):
        return f"Nombre común: {self.nom_comunes}, Nombre científico: {self.nombre_cientifico} ,Código de especie: {self.cod_especie}"

class Glossary(models.Model):
    id = models.IntegerField(primary_key=True, blank=False)
    word = models.CharField(max_length=100)
    definition = models.TextField()

    class Meta:
        managed = False
        db_table = 'glossary'

    def __str__(self):
        return f"ID: {self.id}, Word: {self.word}, Definition: {self.definition}"
    
class CandidateTrees(models.Model):
    ShortcutIDEV = models.CharField(primary_key=True, max_length=60, blank=True)
    numero_placa = models.IntegerField(blank=True, null=True)
    cod_expediente = models.CharField(max_length=35, blank=True, null=True)
    cod_especie = models.CharField(max_length=50, blank=True, null=True)
    fecha_evaluacion = models.DateField()
    usuario_evaluador = models.CharField(max_length=50, blank=True, null=True)
    departamento = models.CharField(max_length=60, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    nombre_del_predio = models.CharField(max_length=60, blank=True, null=True)
    nombre_propietario = models.CharField(max_length=60, blank=True, null=True)
    corregimiento = models.CharField(max_length=60, blank=True, null=True)
    vereda = models.CharField(max_length=60, blank=True, null=True)
    correo = models.CharField(max_length=100, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    altitud = models.IntegerField()
    latitud = models.CharField(max_length=1, blank=True, null=True)
    g_lat = models.IntegerField()
    m_lat = models.IntegerField()
    s_lat = models.CharField(max_length=4, blank=True, null=True)
    longitud = models.CharField(max_length=1, blank=True, null=True)
    g_long = models.IntegerField()
    m_long = models.IntegerField()
    s_long = models.CharField(max_length=4, blank=True, null=True)
    coordenadas_decimales = models.CharField(max_length=150, blank=True, null=True)
    abcisa_xy = models.CharField(max_length=255, blank=True, null=True)
    altura_total = models.CharField(max_length=15, blank=True, null=True)
    altura_comercial = models.CharField(max_length=15, blank=True, null=True)
    cap = models.CharField(max_length=15, blank=True, null=True)
    cobertura = models.CharField(max_length=100, blank=True, null=True)
    cober_otro = models.CharField(max_length=30, blank=True, null=True)
    dominancia_if = models.CharField(max_length=16, blank=True,null=True)
    forma_fuste = models.CharField(max_length=40, blank=True, null=True)
    dominancia = models.CharField(max_length=70, blank=True, null=True)
    alt_bifurcacion = models.CharField(max_length=40, blank=True, null=True)
    estado_copa = models.CharField(max_length=30, blank=True, null=True)
    posicion_copa = models.CharField(max_length=40, blank=True, null=True)
    fitosanitario = models.CharField(max_length=40, blank=True, null=True)
    presencia = models.CharField(max_length=70, blank=True, null=True)
    resultado = models.IntegerField()
    evaluacion = models.CharField(max_length=145, blank=True, null=True)
    observaciones = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'evaluacion_as'

class Monitoring(models.Model):
    IDmonitoreo = models.CharField(primary_key=True, max_length=50)  # Field name made lowercase.
    ShortcutIDEV = models.CharField(max_length=50)  # Field name made lowercase.
    fecha_monitoreo = models.DateField(blank=True, null=True)
    hora = models.TimeField(blank=True, null=True)
    usuario_realiza_monitoreo = models.CharField(db_column='Usuario quien realiza el monitoreo', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    temperatura = models.CharField(max_length=10, blank=True, null=True)
    humedad = models.CharField(max_length=10, blank=True, null=True)
    precipitacion = models.CharField(max_length=13, blank=True, null=True)
    factor_climatico = models.CharField(max_length=20, blank=True, null=True)
    observaciones_temp = models.CharField(max_length=255, blank=True, null=True)
    cap = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    altura_total = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    altura_comercial = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    eje_x = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    eje_y = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    eje_z = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    fitosanitario = models.CharField(max_length=7, blank=True, null=True)
    afectacion = models.CharField(max_length=500, blank=True, null=True)
    observaciones_afec = models.CharField(max_length=200, blank=True, null=True)
    follaje = models.CharField(max_length=50, blank=True, null=True)
    follaje_porcentaje = models.CharField(max_length=50, blank=True, null=True)
    ren_caducifolio = models.CharField(max_length=25, blank=True, null=True)
    observaciones_follaje = models.CharField(max_length=255, blank=True, null=True)
    flor_abierta = models.CharField(max_length=15, blank=True, null=True)
    flor_boton = models.CharField(max_length=15, blank=True, null=True)
    color_flor = models.CharField(max_length=20, blank=True, null=True)
    color_flor_otro = models.CharField(max_length=50, blank=True, null=True)
    olor_flor = models.CharField(max_length=30, blank=True, null=True)
    olor_flor_otro = models.CharField(max_length=50, blank=True, null=True)
    fauna_flor = models.CharField(max_length=30, blank=True, null=True)
    fauna_flor_otros = models.CharField(max_length=50, blank=True, null=True)
    observaciones_flor = models.CharField(max_length=200, blank=True, null=True)
    frutos_verdes = models.CharField(max_length=15, blank=True, null=True)
    estado_madurez = models.CharField(max_length=15, blank=True, null=True)
    color_fruto = models.CharField(max_length=20, blank=True, null=True)
    color_fruto_otro = models.CharField(max_length=50, blank=True, null=True)
    cant_frutos = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True)
    medida_peso_frutos = models.CharField(max_length=30, blank=True, null=True)
    peso_frutos = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True)
    largo_fruto = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    ancho_fruto = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    fauna_frutos = models.CharField(max_length=30, blank=True, null=True)
    fauna_frutos_otro = models.CharField(max_length=50, blank=True, null=True)
    observacion_frutos = models.CharField(max_length=200, blank=True, null=True)
    cant_semillas = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    medida_peso_sem = models.CharField(max_length=30, blank=True, null=True)
    peso_semillas = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    largo_semilla = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    ancho_semilla = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    observacion_semilla = models.CharField(max_length=200, blank=True, null=True)
    entorno = models.CharField(max_length=51, blank=True, null=True)
    entorno_otro = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'monitoreo'

class Samples(models.Model):
    nro_placa = models.CharField(max_length=11, blank=True, null=True)
    fecha_coleccion = models.DateField(blank=True, null=True)
    nro_muestras = models.CharField(max_length=5, blank=True, null=True)
    colector_ppal = models.CharField(max_length=120, blank=True, null=True)
    siglas_colector_ppal = models.CharField(max_length=20, blank=True, null=True)
    nro_coleccion = models.IntegerField(blank=True, null=True)
    voucher = models.CharField(max_length=20, blank=True, null=True)
    nombres_colectores = models.TextField(blank=True, null=True)
    codigo_muestra = models.CharField(max_length=255, blank=True, null=True)
    otros_nombres = models.CharField(max_length=255, null=True)
    descripcion = models.TextField(blank=True, null=True)
    usos = models.TextField(blank=True, null=True)
    familia_especie = models.CharField(max_length=50, null=True)
    nombre_cientifico_muestra = models.CharField(max_length=100, blank=True, null=True)
    up_nombre_cientifico = models.CharField(max_length=200, blank=True, null=True)
    observacion = models.CharField(max_length=300, blank=True, null=True)
    verificado = models.CharField(max_length=15, blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'muestras'

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

"""
CharField: Campo de texto de longitud variable.
TextField: Campo de texto de longitud variable (para textos más largos).
IntegerField: Campo para números enteros.
FloatField: Campo para números de punto flotante.
BooleanField: Campo para valores booleanos (verdadero o falso).
DateField: Campo para almacenar fechas.
DateTimeField: Campo para almacenar fechas y horas.
TimeField: Campo para almacenar horas.
EmailField: Campo para almacenar direcciones de correo electrónico.
URLField: Campo para almacenar URLs.
FileField: Campo para cargar y almacenar archivos.
ImageField: Campo para cargar y almacenar imágenes.
ForeignKey: Campo para representar una relación de clave externa a otro modelo.
ManyToManyField: Campo para representar una relación de muchos a muchos con otros modelos.
"""