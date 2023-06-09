from django.db import models
from django.contrib.auth.models import User


class Assignation(models.Model):
    shortcutnameid = models.CharField(db_column='ShortcutNameID', max_length=100, blank=True, null=True)  # Field name made lowercase.
    shortcutid = models.CharField(db_column='ShortcutID', max_length=100, blank=True, null=True)  # Field name made lowercase.
    username = models.CharField(db_column='UserName', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'assignation'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class ConEmpirico(models.Model):
    id = models.CharField(max_length=20, blank=True, null=True)
    cod_especie = models.CharField(max_length=150, blank=True, null=True)
    fecha_encuesta = models.DateField(blank=True, null=True)
    entrevistador = models.CharField(db_column='Entrevistador', max_length=150, blank=True, null=True)  # Field name made lowercase.
    nombres = models.CharField(max_length=150, blank=True, null=True)
    tipo_documento = models.CharField(max_length=50, blank=True, null=True)
    num_documento = models.CharField(max_length=20, blank=True, null=True)
    edad = models.CharField(max_length=10, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    correo = models.CharField(max_length=60, blank=True, null=True)
    ocupacion = models.CharField(max_length=60, blank=True, null=True)
    rol_cadena = models.CharField(max_length=254, blank=True, null=True)
    nombres_comunes = models.CharField(max_length=200, blank=True, null=True)
    distribucion_geo = models.CharField(max_length=200, blank=True, null=True)
    color_corteza = models.CharField(max_length=60, blank=True, null=True)
    crecimiento = models.CharField(max_length=8, blank=True, null=True)
    longevidad = models.CharField(max_length=40, blank=True, null=True)
    caract_copa = models.TextField(blank=True, null=True)
    car_hojas = models.CharField(max_length=100, blank=True, null=True)
    inicio_flor = models.CharField(max_length=15, blank=True, null=True)
    fin_flor = models.CharField(max_length=15, blank=True, null=True)
    periodo_flor = models.CharField(max_length=12, blank=True, null=True)
    observacion_flor = models.CharField(max_length=255, blank=True, null=True)
    color_flor = models.CharField(max_length=20, blank=True, null=True)
    olor_flor = models.CharField(max_length=20, blank=True, null=True)
    polinizacion = models.CharField(max_length=12, blank=True, null=True)
    obs_flor = models.CharField(max_length=255, blank=True, null=True)
    fauna = models.CharField(max_length=12, blank=True, null=True)
    cual_fauna = models.CharField(max_length=100, blank=True, null=True)
    inicio_fruto = models.CharField(max_length=15, blank=True, null=True)
    fin_fruto = models.CharField(max_length=15, blank=True, null=True)
    periodo_fruto = models.CharField(max_length=12, blank=True, null=True)
    epoca_cos = models.CharField(max_length=50, blank=True, null=True)
    obs_fruto = models.CharField(max_length=255, blank=True, null=True)
    form_fruto = models.CharField(max_length=50, blank=True, null=True)
    color_fruto = models.CharField(max_length=20, blank=True, null=True)
    olor_fruto = models.CharField(max_length=30, blank=True, null=True)
    cant_fruto = models.CharField(max_length=10, blank=True, null=True)
    fauna_fruto = models.CharField(max_length=12, blank=True, null=True)
    cual_fruto = models.CharField(max_length=100, blank=True, null=True)
    form_semillas = models.CharField(max_length=100, blank=True, null=True)
    color_sem = models.CharField(max_length=20, blank=True, null=True)
    olor_sem = models.CharField(max_length=25, blank=True, null=True)
    cant_sem = models.CharField(max_length=10, blank=True, null=True)
    epoca_cosecha = models.CharField(max_length=20, blank=True, null=True)
    fauna_sem = models.CharField(max_length=12, blank=True, null=True)
    cual_fauna_s = models.CharField(max_length=100, blank=True, null=True)
    recoleccion = models.CharField(max_length=40, blank=True, null=True)
    herramientas = models.CharField(max_length=100, blank=True, null=True)
    afectaciones = models.CharField(max_length=100, blank=True, null=True)
    cuidados = models.CharField(max_length=100, blank=True, null=True)
    obs_recol = models.CharField(max_length=255, blank=True, null=True)
    tipo_suelo = models.CharField(max_length=10, blank=True, null=True)
    op_suelo = models.CharField(max_length=25, blank=True, null=True)
    car_suelo = models.CharField(max_length=100, blank=True, null=True)
    abundancia = models.CharField(max_length=100, blank=True, null=True)
    esp_vegetal = models.CharField(max_length=100, blank=True, null=True)
    plagas = models.CharField(max_length=100, blank=True, null=True)
    labor_plagas = models.CharField(max_length=100, blank=True, null=True)
    uso_especie = models.TextField(blank=True, null=True)
    cual_uso = models.CharField(max_length=100, blank=True, null=True)
    consumo_frutos = models.CharField(max_length=20, blank=True, null=True)
    restauracion = models.CharField(max_length=50, blank=True, null=True)
    obs_general = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'con_empirico'


class Configuracion(models.Model):
    shortcutid = models.CharField(db_column='ShortcutID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    nombre = models.CharField(max_length=50, blank=True, null=True)
    icono = models.CharField(max_length=50, blank=True, null=True)
    ref = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'configuracion'


class Data(models.Model):
    livianos = models.CharField(max_length=20, blank=True, null=True)
    medio = models.CharField(max_length=25, blank=True, null=True)
    pesados = models.CharField(max_length=25, blank=True, null=True)
    legumbre = models.CharField(max_length=20, blank=True, null=True)
    leg_plana = models.CharField(max_length=25, blank=True, null=True)
    leg_cilindrica = models.CharField(max_length=30, blank=True, null=True)
    planas = models.CharField(max_length=20, blank=True, null=True)
    tridimensionales = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'data'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class EspecieForestal(models.Model):
    shortcutid = models.CharField(db_column='ShortcutID', max_length=60, blank=True, null=True)  # Field name made lowercase.
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
        return self.cod_especie

class EspeciesSisa(models.Model):
    codigo = models.IntegerField(blank=True, null=True)
    nombre_cientifico = models.CharField(max_length=200, blank=True, null=True)
    flia_apg = models.CharField(max_length=60, blank=True, null=True)
    flia_cronquist = models.CharField(max_length=60, blank=True, null=True)
    clasificacion_res = models.CharField(max_length=60, blank=True, null=True)
    nom_cient_res = models.CharField(max_length=200, blank=True, null=True)
    nombres_comunes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'especies_sisa'


class EvaluacionAs(models.Model):
    shortcutidev = models.CharField(db_column='ShortcutIDEV', max_length=60)  # Field name made lowercase.
    numero_placa = models.IntegerField(blank=True, null=True)
    cod_expediente = models.CharField(max_length=35, blank=True, null=True)
    cod_especie = models.CharField(max_length=50, blank=True, null=True)
    fecha_evaluacion = models.DateField(blank=True, null=True)
    usuario_evaluador = models.CharField(max_length=50, blank=True, null=True)
    departamento = models.CharField(max_length=60, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    nombre_del_predio = models.CharField(max_length=60, blank=True, null=True)
    nombre_propietario = models.CharField(max_length=60, blank=True, null=True)
    corregimiento = models.CharField(max_length=60, blank=True, null=True)
    vereda = models.CharField(max_length=60, blank=True, null=True)
    correo = models.CharField(max_length=100, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    altitud = models.IntegerField(blank=True, null=True)
    latitud = models.CharField(max_length=1, blank=True, null=True)
    g_lat = models.IntegerField(blank=True, null=True)
    m_lat = models.IntegerField(blank=True, null=True)
    s_lat = models.CharField(max_length=4, blank=True, null=True)
    longitud = models.CharField(max_length=1, blank=True, null=True)
    g_long = models.IntegerField(blank=True, null=True)
    m_long = models.IntegerField(blank=True, null=True)
    s_long = models.CharField(max_length=4, blank=True, null=True)
    coordenadas_decimales = models.CharField(max_length=150, blank=True, null=True)
    abcisa_xy = models.CharField(max_length=255, blank=True, null=True)
    altura_total = models.CharField(max_length=15, blank=True, null=True)
    altura_comercial = models.CharField(max_length=15, blank=True, null=True)
    cap = models.CharField(max_length=15, blank=True, null=True)
    cobertura = models.CharField(max_length=100, blank=True, null=True)
    cober_otro = models.CharField(max_length=30, blank=True, null=True)
    dominancia_if = models.CharField(max_length=16, blank=True, null=True)
    forma_fuste = models.CharField(max_length=40, blank=True, null=True)
    dominancia = models.CharField(max_length=70, blank=True, null=True)
    alt_bifurcacion = models.CharField(max_length=40, blank=True, null=True)
    estado_copa = models.CharField(max_length=30, blank=True, null=True)
    posicion_copa = models.CharField(max_length=40, blank=True, null=True)
    fitosanitario = models.CharField(max_length=40, blank=True, null=True)
    presencia = models.CharField(max_length=70, blank=True, null=True)
    resultado = models.IntegerField(blank=True, null=True)
    evaluacion = models.CharField(max_length=145, blank=True, null=True)
    observaciones = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField()
    updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'evaluacion_as'

class Gestionuser(models.Model):
    shortcutid = models.CharField(db_column='ShortcutID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    nombre = models.CharField(max_length=50, blank=True, null=True)
    ref = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gestionuser'


class Location(models.Model):
    putumayo = models.CharField(max_length=60, blank=True, null=True)
    caqueta = models.CharField(max_length=100, blank=True, null=True)
    amazonas = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'location'


class Locations(models.Model):
    cod_dep = models.CharField(max_length=3, blank=True, null=True)
    departamento = models.CharField(max_length=15, blank=True, null=True)
    cod_mun = models.CharField(max_length=5, blank=True, null=True)
    municipio = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'locations'


class ModuloMuestras(models.Model):
    shortcutid = models.CharField(db_column='ShortcutID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    nombre = models.CharField(max_length=50, blank=True, null=True)
    ref = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'modulo_muestras'


class Modulos(models.Model):
    shortcutid = models.CharField(db_column='ShortcutID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    nombre = models.CharField(max_length=100, db_collation='latin1_swedish_ci', blank=True, null=True)
    icono = models.CharField(max_length=100, db_collation='latin1_swedish_ci', blank=True, null=True)
    ref = models.CharField(max_length=100, db_collation='latin1_swedish_ci', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'modulos'


class Monitoreo(models.Model):
    idmonitoreo = models.CharField(db_column='IDmonitoreo', primary_key=True, max_length=50)  # Field name made lowercase.
    shortcutidev = models.CharField(db_column='ShortcutIDEV', max_length=50)  # Field name made lowercase.
    fecha_monitoreo = models.DateField(blank=True, null=True)
    hora = models.TimeField(blank=True, null=True)
    usuario_quien_realiza_el_monitoreo = models.CharField(db_column='Usuario quien realiza el monitoreo', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
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
    medida_cant_frutos = models.CharField(max_length=30, blank=True, null=True)
    cant_frutos = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True)
    medida_peso_frutos = models.CharField(max_length=30, blank=True, null=True)
    peso_frutos = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True)
    largo_fruto = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    ancho_fruto = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    fauna_frutos = models.CharField(max_length=30, blank=True, null=True)
    fauna_frutos_otro = models.CharField(max_length=50, blank=True, null=True)
    observacion_frutos = models.CharField(max_length=200, blank=True, null=True)
    medida_cant_sem = models.CharField(max_length=30, blank=True, null=True)
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

class Muestras(models.Model):
    nro_placa = models.CharField(max_length=11, blank=True, null=True)
    fecha_coleccion = models.DateField(blank=True, null=True)
    nro_muestras = models.CharField(max_length=5, blank=True, null=True)
    colector_ppal = models.CharField(max_length=120, blank=True, null=True)
    siglas_colector_ppal = models.CharField(max_length=20, blank=True, null=True)
    nro_coleccion = models.IntegerField(blank=True, null=True)
    voucher = models.CharField(max_length=20, blank=True, null=True)
    nombres_colectores = models.TextField(blank=True, null=True)
    codigo_muestra = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    usos = models.TextField(blank=True, null=True)
    nombre_cientifico_muestra = models.CharField(max_length=100, blank=True, null=True)
    up_nombre_cientifico = models.CharField(max_length=200, blank=True, null=True)
    observacion = models.CharField(max_length=300, blank=True, null=True)
    verificado = models.CharField(max_length=15, blank=True, null=True)
    cretaed = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'muestras'


class Shortcutroles(models.Model):
    shortcutrolesid = models.CharField(db_column='ShortcutRolesID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    shortcutid = models.CharField(db_column='ShortcutID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    userrole = models.CharField(db_column='UserRole', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'shortcutroles'


class Users(models.Model):
    userid = models.CharField(db_column='UserID', primary_key=True, max_length=50)  # Field name made lowercase.
    useremail = models.CharField(db_column='UserEmail', max_length=50, blank=True, null=True)  # Field name made lowercase.
    username = models.CharField(db_column='UserName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    userrol = models.CharField(db_column='UserRol', max_length=100, blank=True, null=True)  # Field name made lowercase.
    useractive = models.CharField(db_column='UserActive', max_length=30, blank=True, null=True)  # Field name made lowercase.
    tipo_documento = models.CharField(max_length=40, blank=True, null=True)
    nro_documento = models.CharField(max_length=20, blank=True, null=True)
    entidad = models.CharField(max_length=100, blank=True, null=True)
    celular = models.CharField(max_length=15, blank=True, null=True)
    departamento = models.CharField(max_length=25, blank=True, null=True)
    equipo_celular = models.CharField(db_column='Equipo Celular', max_length=2, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    serial = models.CharField(db_column='Serial', max_length=17, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'users'
