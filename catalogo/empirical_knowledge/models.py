from django.db import models

class EmpiricalKnowledge(models.Model):
    id = models.CharField(primary_key=True, max_length=60)
    cod_especie = models.CharField(max_length=50, blank=True, null=True)
    fecha_encuesta = models.DateField()
    hora_encuesta = models.TimeField(blank=True, null=True)
    user_id = models.IntegerField()
    tipo_usuario = models.CharField(max_length=50, blank=True, null=True)
    otro_tipo_usuario = models.CharField(max_length=150, blank=True, null=True)
    nombres = models.CharField(max_length=150, blank=True, null=True)
    tipo_documento = models.CharField(max_length=50, blank=True, null=True)
    num_documento = models.CharField(max_length=20, blank=True, null=True)
    edad = models.CharField(max_length=10, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    correo = models.CharField(max_length=60, blank=True, null=True)
    departamento = models.CharField(max_length=150, blank=True, null=True)
    municipio = models.CharField(max_length=150, blank=True, null=True)
    nombre_predio = models.CharField(max_length=150, blank=True, null=True)
    vereda = models.CharField(max_length=150, blank=True, null=True)
    predios_recoleccion = models.TextField(blank=True, null=True)
    tenencia_predio = models.CharField(max_length=30, blank=True, null=True)
    no_propiedad_predio = models.TextField(blank=True, null=True)
    personas_predio = models.TextField(blank=True, null=True)
    acceso_predio = models.TextField(blank=True, null=True)
    numero_placa = models.IntegerField(blank=True, null=True)
    nombres_comunes = models.CharField(max_length=200, blank=True, null=True)
    crecimiento = models.CharField(max_length=8, blank=True, null=True)
    zonas_individuo = models.CharField(max_length=255, blank=True, null=True)
    max_diametro = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    max_altura = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    amplitud_copa = models.CharField(max_length=30, blank=True, null=True)
    observaciones_copa = models.TextField(blank=True, null=True)
    informacion_hojas = models.CharField(max_length=500, blank=True, null=True)
    inicio_flor = models.CharField(max_length=150, blank=True, null=True)
    fin_flor = models.CharField(max_length=150, blank=True, null=True)
    estacionalidad_floracion = models.CharField(max_length=12, blank=True, null=True)
    estacionalidad_floracion_otro = models.CharField(max_length=50, blank=True, null=True)
    tipo_floracion = models.CharField(max_length=50, blank=True, null=True)
    informacion_flor = models.TextField(blank=True, null=True)
    fauna_flor = models.CharField(max_length=100, blank=True, null=True)
    descripcion_fauna_flor = models.CharField(max_length=100, blank=True, null=True)
    comportamiento_fauna_flores = models.CharField(max_length=255, blank=True, null=True)
    inicio_fruto = models.CharField(max_length=150, blank=True, null=True)
    fin_fruto = models.CharField(max_length=150, blank=True, null=True)
    tipo_fructificacion = models.CharField(max_length=20, blank=True, null=True)
    otro_tipo_fruct = models.CharField(max_length=50, blank=True, null=True)
    epoca_cosecha_fruto = models.TextField(blank=True, null=True)
    cantidad_frutos_produccion = models.CharField(max_length=255, blank=True, null=True)
    informacion_frutos = models.TextField(blank=True, null=True)
    fauna_fruto = models.CharField(max_length=100, blank=True, null=True)
    descripcion_fruto_otro = models.CharField(max_length=100, blank=True, null=True)
    comportamiento_fauna_frutos = models.TextField(blank=True, null=True)
    inicio_semillas = models.CharField(max_length=150, blank=True, null=True)
    fin_semillas = models.CharField(max_length=150, blank=True, null=True)
    cantidad_semillas = models.CharField(max_length=25, blank=True, null=True)
    descripcion_semillas = models.TextField(blank=True, null=True)
    fauna_semillas = models.CharField(max_length=100, blank=True, null=True)
    descripcion_semillas_otro = models.CharField(max_length=100, blank=True, null=True)
    comportamiento_fauna_semillas = models.TextField(blank=True, null=True)
    germinacion_semillas = models.TextField(blank=True, null=True)
    recoleccion = models.CharField(max_length=40, blank=True, null=True)
    metodo_recoleccion = models.CharField(max_length=254, blank=True, null=True)
    herramientas = models.TextField(blank=True, null=True)
    cantidad_plantulas = models.CharField(max_length=100, blank=True, null=True)
    caracteristicas_plantulas = models.CharField(max_length=255, blank=True, null=True)
    ambiente_plantulas = models.CharField(max_length=255, blank=True, null=True)
    proceso_recoleccion = models.TextField(blank=True, null=True)
    manejo_sostenible = models.TextField(blank=True, null=True)
    preferencia_cosecha = models.TextField(blank=True, null=True)
    afectaciones_recoleccion = models.TextField(blank=True, null=True)
    cuidados_recoleccion = models.TextField(blank=True, null=True)
    practicas_conservacion = models.TextField(blank=True, null=True)
    normas_aprovechamiento = models.TextField(blank=True, null=True)
    afectaciones_cosecha_plantas = models.TextField(blank=True, null=True)
    afectaciones_cosecha_animales = models.TextField(blank=True, null=True)
    afectaciones_cosecha_agua = models.TextField(blank=True, null=True)
    afectaciones_cosecha_suelo = models.TextField(blank=True, null=True)
    practicas_disminuir_afectaciones = models.TextField(blank=True, null=True)
    abundancia_especie = models.CharField(max_length=100, blank=True, null=True)
    abundancia_especie_diez = models.CharField(max_length=100, blank=True, null=True)
    organizacion_individuos = models.CharField(max_length=100, blank=True, null=True)
    entorno_individuos = models.CharField(max_length=100, blank=True, null=True)
    entorno_individuos_otros = models.TextField(blank=True, null=True)
    crecimiento_individuos = models.CharField(max_length=100, blank=True, null=True)
    durabilidad_individuos = models.CharField(max_length=100, blank=True, null=True)
    plagas_enfermedades = models.TextField(blank=True, null=True)
    control_plagas_enfermedades = models.CharField(max_length=500, blank=True, null=True)
    coberturas_especie = models.CharField(max_length=150, blank=True, null=True)
    coberturas_especie_otro = models.TextField(blank=True, null=True)
    uso_especie = models.CharField(max_length=100, blank=True, null=True)
    uso_especie_otro = models.CharField(max_length=500, blank=True, null=True)
    partes_usadas_planta = models.CharField(max_length=500, blank=True, null=True)
    partes_usadas_planta_otro = models.CharField(max_length=255, blank=True, null=True)
    descripcion_uso_especie = models.TextField(blank=True, null=True)
    frecuencia_uso_especie = models.CharField(max_length=20, blank=True, null=True)
    conocimiento_transmision = models.CharField(max_length=20, blank=True, null=True)
    porque_conocimiento_transmision = models.TextField(blank=True, null=True)
    quienes_conocimiento = models.CharField(max_length=255, blank=True, null=True)
    uso_especie_diez = models.CharField(max_length=50, blank=True, null=True)
    consumo_especie_fauna = models.CharField(max_length=60, blank=True, null=True)
    informacion_general = models.TextField(blank=True, null=True)
    alm_semilla_campo = models.CharField(max_length=500, blank=True, null=True)
    alm_semilla_vivero = models.CharField(max_length=500, blank=True, null=True)
    tratamientos_semillas = models.CharField(max_length=500, blank=True, null=True)
    manejo_plantulas_campo = models.CharField(max_length=500, blank=True, null=True)
    metodos_propagacion = models.CharField(max_length=500, blank=True, null=True)
    tratamientos_pre_propagacion = models.CharField(max_length=500, blank=True, null=True)
    recomendaciones_cuidados = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'con_empirico'