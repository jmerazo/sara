from django.urls import path
from .speciesForrests import EspecieForestalView, NombresComunesView, FamiliaView, NombreCientificoView, suggestion_type_view, BuscarEspecieView, BuscarFamiliaView, FamiliasView, ScientificNameView, ReportSpecieDataView, SearchCandidatesSpecieView
from ..helpers.pdf_export import ExportSpecies # Importa la función para exportar perfil de especie forestal en PDF

# LISTADO DE URLS PARA ESPECIES FORESTALES
urlpatterns = [
    path('', EspecieForestalView.as_view()), # Lista todas las especies registradas -- http://localhost:8000/api/species/
    path('common_name', NombresComunesView.as_view({'get' : 'list'})), # Validar y eliminar -- http://localhost:8000/api/species/common_name
    path('family/filter', FamiliaView.as_view()), # Validar y eliminar -- http://localhost:8000/api/species/family/filter
    path('scientific_names', NombreCientificoView.as_view({'get' : 'list'})), # retorna la lista de nombres científicos -- http://localhost:8000/api/species/scientific_names
    path('search/scientific_name/<str:scientific>', ScientificNameView.as_view()), # Busca una especie por su nombre científico -- http://localhost:8000/api/species/search/scientific_name/Bauhinia%20tarapotensis%20Benth.
    path('suggestion/<str:types>', suggestion_type_view), # retorna listado de sugerencias por nombre_común, familia y nombres_científicos -- http://localhost:8000/api/species/suggestion/familia
    path('search/code/<int:code>', BuscarEspecieView.as_view()), # Busca una especie por su código -- http://localhost:8000/api/species/code/789
    path('families', FamiliasView.as_view()), # Lista las especies relacionadas a cada familia -- http://localhost:8000/api/species/families
    path('search/family/<str:family>', BuscarFamiliaView.as_view()), # Retorna las especies buscadas por su nombre de familia -- http://localhost:8000/api/species/search/family/BIGNONIACEAE
    path('profile/export/<int:code>', ExportSpecies.as_view()), # Exporta en PDF el perfil de la especie forestal -- http://localhost:8000/api/species/perfil/export/789
    path('report/general', ReportSpecieDataView.as_view()), # Retorna la cantidad realizada de monitoreos, muestras y evaluaciones -- http://localhost:8000/api/species/report/general
    path('candidates/search/<str:nom>', SearchCandidatesSpecieView.as_view()), # Busca y retorn los individuos evaluados de cada especie en base a su nombre común -- http://localhost:8000/api/species/candidates/search/name_specie
]