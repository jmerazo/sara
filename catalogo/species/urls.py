from django.urls import path
from .speciesForrests import SpecieForrestView, FamiliesView, SearchSpecieForrestView, SearchFamilyView, ReportSpecieDataView, SearchCandidatesSpecieView
from ..helpers.pdf_export import ExportSpecies # Importa la función para exportar perfil de especie forestal en PDF

# LISTADO DE URLS PARA ESPECIES FORESTALES
urlpatterns = [
    path('', SpecieForrestView.as_view()), # Lista todas las especies registradas -- http://localhost:8000/api/species/
    path('<str:pk>', SpecieForrestView.as_view()),
    path('search/code/<int:code>', SearchSpecieForrestView.as_view()), # Busca una especie por su código -- http://localhost:8000/api/species/code/789
    path('families/', FamiliesView.as_view()), # Lista las especies relacionadas a cada familia -- http://localhost:8000/api/species/families
    path('search/family/<str:family>', SearchFamilyView.as_view()), # Retorna las especies buscadas por su nombre de familia -- http://localhost:8000/api/species/search/family/BIGNONIACEAE
    path('profile/export/<int:code>', ExportSpecies.as_view()), # Exporta en PDF el perfil de la especie forestal -- http://localhost:8000/api/species/perfil/export/789
    path('report/general', ReportSpecieDataView.as_view()), # Retorna la cantidad realizada de monitoreos, muestras y evaluaciones -- http://localhost:8000/api/species/report/general
    path('candidates/search/<str:nom>', SearchCandidatesSpecieView.as_view()), # Busca y retorn los individuos evaluados de cada especie en base a su nombre común -- http://localhost:8000/api/species/candidates/search/name_specie
]