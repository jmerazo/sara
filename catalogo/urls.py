from django.urls import path
from .views import EspecieForestalView, NombresComunesView, CandidatesTreesView, SearchCandidatesSpecieView, MonitoringsView, SearchMonitoringCandidateView, ReportSpecieDataView, SearchMonitoringSpecieView, FamiliaView, NombreCientificoView, suggestion_type_view, BuscarEspecieView, BuscarFamiliaView, FamiliasView, ScientificNameView, GlossaryView, GeoCandidateTreesView, AverageCandidateTreesView, LoginView, LogoutView, PageView, SamplesView
from .helpers.pdf_export import ExportSpecies
from .helpers.excel_export import ExportCandidateTrees
from .reports.monitoring import MonitoringReport, MonitoringReportLocates, MonitoringReportTotal
from .reports.samples import SamplesReport
from .administration.users import UsersView, UsersStateView
from .helpers.locates import DepartmentsView, CitiesView


urlpatterns = [
    path('especie_forestal/', EspecieForestalView.as_view()),
    path('especie_forestal/<str:pk>', EspecieForestalView.as_view()),
    path('especie_forestal/nombres_comunes', NombresComunesView.as_view({
        'get' : 'list'
    })),
    path('especie_forestal/familia/filter', FamiliaView.as_view()),
    path('especie_forestal/nombres_cientificos', NombreCientificoView.as_view({
        'get' : 'list'
    })),
    path('especie_forestal/suggestion/<str:types>', suggestion_type_view),
    path('especie_forestal/search/nombre_comun/<int:code>', BuscarEspecieView.as_view()),
    path('especie_forestal/search/familia/<str:familia>', BuscarFamiliaView.as_view()),
    path('especie_forestal/familias', FamiliasView.as_view()),
    path('especie_forestal/search/scientificname/<str:scientific>', ScientificNameView.as_view()),
    path('glossary', GlossaryView.as_view()),
    path('candidate/geolocation', GeoCandidateTreesView.as_view()),
    path('candidate/average', AverageCandidateTreesView.as_view()),

    path('especie_forestal/export/<int:code>', ExportSpecies.as_view(), name='export-species'),
    path('candidate/export/all', ExportCandidateTrees.as_view(), name='export-candidates'),

    # REPORTE DE MONITOREOS MENSUALES POR MUNICIPIO, DEPARTAMENTO Y GENERAL
    path('monitoring/report/month', MonitoringReport.as_view(), name='monitoring-report'),
    path('monitoring/report/month/locates', MonitoringReportLocates.as_view(), name='monitoring-rl'),
    path('monitoring/report/general/total', MonitoringReportTotal.as_view(), name='monitoring-tl'),

    path('monitoring/report/data', MonitoringsView.as_view()), # Exporta todos los datos de monitoreos

    # URLS: SAMPLES
    path('samples/report/general', SamplesReport.as_view()),
    path('samples/report/data', SamplesView.as_view()), # Exporta todos los datos de las muestras

    # CONSULTA DE MONITOREOS POR INDIVIDUO
    path('candidates/search/monitorings/<id>', SearchMonitoringCandidateView.as_view()), # genera el listado de monitoreos del individuo consultado
    path('monitoring/search/specie/<int:code>', SearchMonitoringSpecieView.as_view()), # genera el listado de monitoreos por la especie consultada

    path('candidates/trees', CandidatesTreesView.as_view()), # Lista los individuos evaluados totales
    path('specie/report/data', ReportSpecieDataView.as_view()), # Genera el reporte de cantidad de individuos evaluados, monitoreos y muestras por especie
    path('specie/search/candidates/<str:nom>', SearchCandidatesSpecieView.as_view()), # Busca los individuos evaluados de cada especie en base a su nombre común

    path('auth/login/', LoginView.as_view()),
    path('auth/logout/', LogoutView.as_view()),

    path('page/content', PageView.as_view(), name='page-list'),
    path('page/content/<int:pk>', PageView.as_view(), name='page-detail'),

    path('users/', UsersView.as_view()),
    path('users/<int:pk>', UsersView.as_view()),
    path('users/state/<int:pk>', UsersStateView.as_view()),

    path('departments/', DepartmentsView.as_view()),
    path('cities/', CitiesView.as_view())
]