from django.urls import path
from .views import EspecieForestalView, NombresComunesView, FamiliaView, NombreCientificoView, suggestion_type_view, BuscarEspecieView, BuscarFamiliaView, FamiliasView, ScientificNameView, GlossaryView, GeoCandidateTreesView, AverageCandidateTreesView

urlpatterns = [
    path('especie_forestal/', EspecieForestalView.as_view({
        'get' : 'list',
        'post' : 'create',
        'delete': 'destroy',
        'put': 'update'
    })),
    path('especie_forestal/nombres_comunes', NombresComunesView.as_view({
        'get' : 'list'
    })),
    path('especie_forestal/familia', FamiliaView.as_view({
        'get' : 'list'
    })),
    path('especie_forestal/nombres_cientificos', NombreCientificoView.as_view({
        'get' : 'list'
    })),
    path('especie_forestal/suggestion/<str:types>', suggestion_type_view),
    path('especie_forestal/search/nombre_comun/<str:nombre>', BuscarEspecieView.as_view()),
    path('especie_forestal/search/familia/<str:familia>', BuscarFamiliaView.as_view()),
    path('especie_forestal/familias', FamiliasView.as_view()),
    path('especie_forestal/search/scientificname/<str:scientific>', ScientificNameView.as_view()),
    path('glossary', GlossaryView.as_view()),
    path('candidate/geolocation', GeoCandidateTreesView.as_view()),
    path('candidate/average', AverageCandidateTreesView.as_view())
]