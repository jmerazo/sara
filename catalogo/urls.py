from django.urls import path
from .views import EspecieForestalView, NombresComunesView, FamiliaView, NombreCientificoView, suggestion_type_view, BuscarEspecieView

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
    path('especie_forestal/search/nombre_comun/<str:nombre>', BuscarEspecieView.as_view())
]