from django.urls import path
from .monitorings import MonitoringsView, SearchMonitoringCandidateView, SearchMonitoringSpecieView
from .reports import MonitoringReport, MonitoringReportLocates, MonitoringReportTotal

urlpatterns = [
    # REPORTE DE MONITOREOS MENSUALES POR MUNICIPIO, DEPARTAMENTO Y GENERAL
    path('report/month', MonitoringReport.as_view()), # (PROTECT) Retorna la cantidad mensual de monitoreos realizados, pendientes y total -- http://localhost:8000/api/monitoring/report/month
    path('report/month/locates', MonitoringReportLocates.as_view()), # (PROTECT) Retorna la cantidad mensual de monitoreos realizados, pendientes y total por municipios -- http://localhost:8000/api/monitoring/report/month/locates
    path('report/general/total', MonitoringReportTotal.as_view()),  # (PROTECT) Retorna la cantidad mensual de monitoreos realizados, pendientes y total por municipios -- http://localhost:8000/api/monitoring/report/general/total
    path('report/data', MonitoringsView.as_view()), # Exporta todos los datos de monitoreos en excel -- http://localhost:8000/api/monitoring/report/data

    # CONSULTA DE MONITOREOS POR INDIVIDUO
    path('candidate/search/<id>', SearchMonitoringCandidateView.as_view()), # Retorna el listado de monitoreos del individuo consultado -- http://localhost:8000/api/monitoring/search/
    path('specie/search/<int:code>', SearchMonitoringSpecieView.as_view()), # Retorna el listado de monitoreos por la especie consultada -- http://localhost:8000/api/monitoring/specie/search/code_especie
]