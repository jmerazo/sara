from django.db import models
from ..property.models import Property
from ..species.models import SpecieForrest
from ..models import Users

class CandidatesTrees(models.Model):
    id = models.CharField(primary_key=True, max_length=60)
    institutionCode = models.CharField(max_length=100, blank=True, null=True)
    institutionID = models.CharField(max_length=100, blank=True, null=True)
    identificador = models.CharField(max_length=10, blank=True, null=True)
    numero_placa = models.IntegerField(blank=True, null=True)
    cod_expediente = models.CharField(max_length=35, blank=True, null=True)
    cod_especie = models.ForeignKey(SpecieForrest, on_delete=models.RESTRICT, to_field='code_specie', db_column='cod_especie_id', related_name='candidates_trees')
    eventID = models.CharField(max_length=50, blank=True, null=True)
    eventDate = models.DateField(null=True)
    user = models.ForeignKey(Users, on_delete=models.RESTRICT)
    property = models.ForeignKey(Property, on_delete=models.RESTRICT)
    departamento = models.CharField(max_length=60, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    nombre_del_predio = models.CharField(max_length=60, blank=True, null=True)
    nombre_propietario = models.CharField(max_length=60, blank=True, null=True)
    corregimiento = models.CharField(max_length=60, blank=True, null=True)
    locality = models.CharField(max_length=60, blank=True, null=True)
    correo = models.CharField(max_length=100, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    ocurrenceID = models.CharField(max_length=150, blank=True, null=True)
    basisOfRecord = models.CharField(max_length=150, blank=True, null=True)
    type = models.CharField(max_length=30, blank=True, null=True)
    collectionCode = models.CharField(max_length=50, blank=True, null=True)
    collectionID = models.CharField(max_length=50, blank=True, null=True)
    catalogNumber = models.CharField(max_length=50, blank=True, null=True)
    language = models.CharField(max_length=15, blank=True, null=True)
    rightsHolder = models.CharField(max_length=50, blank=True, null=True)
    recordedBy = models.CharField(max_length=150, blank=True, null=True)
    organismRemarks = models.TextField(blank=True, null=True)
    year = models.CharField(max_length=5, blank=True, null=True)
    month = models.CharField(max_length=5, blank=True, null=True)
    day = models.CharField(max_length=5, blank=True, null=True)
    habitat = models.CharField(max_length=150, blank=True, null=True)
    locationID = models.CharField(max_length=150, blank=True, null=True)
    continent = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=10, blank=True, null=True)
    countryCode = models.CharField(max_length=10, blank=True, null=True)
    stateProvince = models.CharField(max_length=100, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    verbatimLocality = models.CharField(max_length=60, blank=True, null=True)
    minimumElevationInMeters = models.IntegerField(blank=True, null=True)
    maximumElevationInMeters = models.IntegerField(blank=True, null=True)
    verbatimCoordinateSystem = models.CharField(max_length=30, blank=True, null=True)
    verbatimLatitude = models.CharField(max_length=20, blank=True, null=True)
    g_lat = models.IntegerField(null=True)
    m_lat = models.IntegerField(null=True)
    s_lat = models.CharField(max_length=4, blank=True, null=True)
    verbatimLongitude = models.CharField(max_length=20, blank=True, null=True)
    g_long = models.IntegerField(null=True)
    m_long = models.IntegerField(null=True)
    s_long = models.CharField(max_length=4, blank=True, null=True)
    decimalLatitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    decimalLongitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    coordenadas_decimales = models.CharField(max_length=150, blank=True, null=True)
    abcisa_xy = models.CharField(max_length=255, blank=True, null=True)
    geodeticDatum = models.CharField(max_length=100, blank=True, null=True)
    cobertura = models.CharField(max_length=100, blank=True, null=True)
    entorno_individuo = models.CharField(max_length=100, blank=True, null=True)
    dominancia_if = models.CharField(max_length=16, blank=True,null=True)
    forma_fuste = models.CharField(max_length=40, blank=True, null=True)
    dominancia = models.CharField(max_length=70, blank=True, null=True)
    alt_bifurcacion = models.CharField(max_length=40, blank=True, null=True)
    estado_copa = models.CharField(max_length=30, blank=True, null=True)
    posicion_copa = models.CharField(max_length=40, blank=True, null=True)
    fitosanitario = models.CharField(max_length=40, blank=True, null=True)
    presencia = models.CharField(max_length=70, blank=True, null=True)
    resultado = models.IntegerField(null=True)
    evaluacion = models.CharField(max_length=145, blank=True, null=True)
    observaciones = models.CharField(max_length=255, blank=True, null=True)
    estado_placa = models.CharField(max_length=25, blank=True, null=True)
    validated = models.CharField(max_length=15, blank=True, null=True)
    recordNumber = models.CharField(max_length=150, blank=True, null=True)
    organismQuantity = models.IntegerField(null=True, blank=True)
    organismQuantityType = models.CharField(max_length=50, blank=True, null=True)
    lifeStage = models.CharField(max_length=50, blank=True, null=True)
    preparations = models.CharField(max_length=50, blank=True, null=True)
    disposition = models.CharField(max_length=50, blank=True, null=True)
    occurrenceRemarks = models.TextField(null=True, blank=True)
    samplingProtocol = models.CharField(max_length=100, blank=True, null=True)
    fieldNumber = models.CharField(max_length=100, blank=True, null=True)
    fieldNotes = models.CharField(max_length=100, blank=True, null=True)
    municipality = models.CharField(max_length=100, blank=True, null=True)
    identifiedBy = models.CharField(max_length=100, blank=True, null=True)
    dateIdentified = models.CharField(max_length=100, blank=True, null=True)
    identificationQualifier = models.CharField(max_length=100, blank=True, null=True)
    datasetName = models.CharField(max_length=70, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'evaluacion_as_c'