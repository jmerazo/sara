# Generated by Django 4.1.1 on 2023-09-30 16:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CandidateTrees',
            fields=[
                ('ShortcutIDEV', models.CharField(blank=True, max_length=60, primary_key=True, serialize=False)),
                ('numero_placa', models.IntegerField(blank=True, null=True)),
                ('cod_expediente', models.CharField(blank=True, max_length=35, null=True)),
                ('cod_especie', models.CharField(blank=True, max_length=50, null=True)),
                ('fecha_evaluacion', models.DateField()),
                ('usuario_evaluador', models.CharField(blank=True, max_length=50, null=True)),
                ('departamento', models.CharField(blank=True, max_length=60, null=True)),
                ('municipio', models.CharField(blank=True, max_length=100, null=True)),
                ('nombre_del_predio', models.CharField(blank=True, max_length=60, null=True)),
                ('nombre_propietario', models.CharField(blank=True, max_length=60, null=True)),
                ('corregimiento', models.CharField(blank=True, max_length=60, null=True)),
                ('vereda', models.CharField(blank=True, max_length=60, null=True)),
                ('correo', models.CharField(blank=True, max_length=100, null=True)),
                ('celular', models.CharField(blank=True, max_length=20, null=True)),
                ('altitud', models.IntegerField()),
                ('latitud', models.CharField(blank=True, max_length=1, null=True)),
                ('g_lat', models.IntegerField()),
                ('m_lat', models.IntegerField()),
                ('s_lat', models.CharField(blank=True, max_length=4, null=True)),
                ('longitud', models.CharField(blank=True, max_length=1, null=True)),
                ('g_long', models.IntegerField()),
                ('m_long', models.IntegerField()),
                ('s_long', models.CharField(blank=True, max_length=4, null=True)),
                ('coordenadas_decimales', models.CharField(blank=True, max_length=150, null=True)),
                ('abcisa_xy', models.CharField(blank=True, max_length=255, null=True)),
                ('altura_total', models.CharField(blank=True, max_length=15, null=True)),
                ('altura_comercial', models.CharField(blank=True, max_length=15, null=True)),
                ('cap', models.CharField(blank=True, max_length=15, null=True)),
                ('cobertura', models.CharField(blank=True, max_length=100, null=True)),
                ('cober_otro', models.CharField(blank=True, max_length=30, null=True)),
                ('dominancia_if', models.CharField(blank=True, max_length=16, null=True)),
                ('forma_fuste', models.CharField(blank=True, max_length=40, null=True)),
                ('dominancia', models.CharField(blank=True, max_length=70, null=True)),
                ('alt_bifurcacion', models.CharField(blank=True, max_length=40, null=True)),
                ('estado_copa', models.CharField(blank=True, max_length=30, null=True)),
                ('posicion_copa', models.CharField(blank=True, max_length=40, null=True)),
                ('fitosanitario', models.CharField(blank=True, max_length=40, null=True)),
                ('presencia', models.CharField(blank=True, max_length=70, null=True)),
                ('resultado', models.IntegerField()),
                ('evaluacion', models.CharField(blank=True, max_length=145, null=True)),
                ('observaciones', models.CharField(blank=True, max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'evaluacion_as',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Cities',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('code', models.CharField(blank=True, max_length=10, null=True)),
                ('name', models.CharField(blank=True, max_length=60, null=True)),
                ('department_id', models.IntegerField()),
            ],
            options={
                'db_table': 'cities',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Departments',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('code', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'departments',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EspecieForestal',
            fields=[
                ('ShortcutID', models.CharField(blank=True, max_length=60, primary_key=True, serialize=False)),
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
        migrations.CreateModel(
            name='Glossary',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('word', models.CharField(max_length=100)),
                ('definition', models.TextField()),
            ],
            options={
                'db_table': 'glossary',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Monitoring',
            fields=[
                ('IDmonitoreo', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('ShortcutIDEV', models.CharField(max_length=50)),
                ('fecha_monitoreo', models.DateField(blank=True, null=True)),
                ('hora', models.TimeField(blank=True, null=True)),
                ('usuario_realiza_monitoreo', models.CharField(blank=True, db_column='Usuario quien realiza el monitoreo', max_length=50, null=True)),
                ('temperatura', models.CharField(blank=True, max_length=10, null=True)),
                ('humedad', models.CharField(blank=True, max_length=10, null=True)),
                ('precipitacion', models.CharField(blank=True, max_length=13, null=True)),
                ('factor_climatico', models.CharField(blank=True, max_length=20, null=True)),
                ('observaciones_temp', models.CharField(blank=True, max_length=255, null=True)),
                ('cap', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('altura_total', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('altura_comercial', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('eje_x', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('eje_y', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('eje_z', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('fitosanitario', models.CharField(blank=True, max_length=7, null=True)),
                ('afectacion', models.CharField(blank=True, max_length=500, null=True)),
                ('observaciones_afec', models.CharField(blank=True, max_length=200, null=True)),
                ('follaje', models.CharField(blank=True, max_length=50, null=True)),
                ('follaje_porcentaje', models.CharField(blank=True, max_length=50, null=True)),
                ('ren_caducifolio', models.CharField(blank=True, max_length=25, null=True)),
                ('observaciones_follaje', models.CharField(blank=True, max_length=255, null=True)),
                ('flor_abierta', models.CharField(blank=True, max_length=15, null=True)),
                ('flor_boton', models.CharField(blank=True, max_length=15, null=True)),
                ('color_flor', models.CharField(blank=True, max_length=20, null=True)),
                ('color_flor_otro', models.CharField(blank=True, max_length=50, null=True)),
                ('olor_flor', models.CharField(blank=True, max_length=30, null=True)),
                ('olor_flor_otro', models.CharField(blank=True, max_length=50, null=True)),
                ('fauna_flor', models.CharField(blank=True, max_length=30, null=True)),
                ('fauna_flor_otros', models.CharField(blank=True, max_length=50, null=True)),
                ('observaciones_flor', models.CharField(blank=True, max_length=200, null=True)),
                ('frutos_verdes', models.CharField(blank=True, max_length=15, null=True)),
                ('estado_madurez', models.CharField(blank=True, max_length=15, null=True)),
                ('color_fruto', models.CharField(blank=True, max_length=20, null=True)),
                ('color_fruto_otro', models.CharField(blank=True, max_length=50, null=True)),
                ('cant_frutos', models.DecimalField(blank=True, decimal_places=0, max_digits=11, null=True)),
                ('medida_peso_frutos', models.CharField(blank=True, max_length=30, null=True)),
                ('peso_frutos', models.DecimalField(blank=True, decimal_places=0, max_digits=11, null=True)),
                ('largo_fruto', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('ancho_fruto', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('fauna_frutos', models.CharField(blank=True, max_length=30, null=True)),
                ('fauna_frutos_otro', models.CharField(blank=True, max_length=50, null=True)),
                ('observacion_frutos', models.CharField(blank=True, max_length=200, null=True)),
                ('cant_semillas', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('medida_peso_sem', models.CharField(blank=True, max_length=30, null=True)),
                ('peso_semillas', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('largo_semilla', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('ancho_semilla', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('observacion_semilla', models.CharField(blank=True, max_length=200, null=True)),
                ('entorno', models.CharField(blank=True, max_length=51, null=True)),
                ('entorno_otro', models.CharField(blank=True, max_length=100, null=True)),
                ('observaciones', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'monitoreo',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('section', models.CharField(blank=True, max_length=50, null=True)),
                ('router', models.CharField(blank=True, max_length=50, null=True)),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('content', models.TextField(blank=True, null=True)),
                ('url', models.CharField(blank=True, max_length=300, null=True)),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'page',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Samples',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nro_placa', models.CharField(blank=True, max_length=11, null=True)),
                ('fecha_coleccion', models.DateField(blank=True, null=True)),
                ('nro_muestras', models.CharField(blank=True, max_length=5, null=True)),
                ('colector_ppal', models.CharField(blank=True, max_length=120, null=True)),
                ('siglas_colector_ppal', models.CharField(blank=True, max_length=20, null=True)),
                ('nro_coleccion', models.IntegerField(blank=True, null=True)),
                ('voucher', models.CharField(blank=True, max_length=20, null=True)),
                ('nombres_colectores', models.TextField(blank=True, null=True)),
                ('codigo_muestra', models.CharField(blank=True, max_length=255, null=True)),
                ('otros_nombres', models.CharField(max_length=255, null=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('usos', models.TextField(blank=True, null=True)),
                ('familia_especie', models.CharField(max_length=50, null=True)),
                ('nombre_cientifico_muestra', models.CharField(blank=True, max_length=100, null=True)),
                ('up_nombre_cientifico', models.CharField(blank=True, max_length=200, null=True)),
                ('observacion', models.CharField(blank=True, max_length=300, null=True)),
                ('verificado', models.CharField(blank=True, max_length=15, null=True)),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'muestras',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('password', models.CharField(blank=True, max_length=150, null=True)),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('rol', models.CharField(blank=True, max_length=100, null=True)),
                ('is_active', models.BooleanField(blank=True, default=False, max_length=30, null=True)),
                ('document_type', models.CharField(blank=True, max_length=40, null=True)),
                ('document_number', models.CharField(blank=True, max_length=20, null=True)),
                ('entity', models.CharField(blank=True, max_length=100, null=True)),
                ('cellphone', models.CharField(blank=True, max_length=15, null=True)),
                ('department', models.CharField(blank=True, max_length=25, null=True)),
                ('city', models.IntegerField(blank=True, null=True)),
                ('device_movile', models.CharField(blank=True, max_length=2, null=True)),
                ('serial_device', models.CharField(blank=True, max_length=17, null=True)),
                ('profession', models.CharField(blank=True, max_length=150, null=True)),
                ('reason', models.CharField(blank=True, max_length=500, null=True)),
                ('state', models.CharField(blank=True, default='REVIEW', max_length=25, null=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_superuser', models.SmallIntegerField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(blank=True, to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, to='auth.permission')),
            ],
            options={
                'db_table': 'Users',
                'managed': True,
            },
        ),
    ]
