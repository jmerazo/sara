from django.urls import path, include
from .utils.utils import GlossaryView
from .helpers.locates import DepartmentsView, CitiesView

urlpatterns = [
    path('glossary', GlossaryView.as_view()),
    path('departments/', DepartmentsView.as_view()),
    path('cities/', CitiesView.as_view()),

    # ===========================================================
    path('users/', include('catalogo.users.urls')),
    path('samples/', include('catalogo.samples.urls')),
    path('candidates/', include('catalogo.candidates.urls')),
    path('monitoring/', include('catalogo.monitorings.urls')),
    path('species/', include('catalogo.species.urls')),
    path('page/', include('catalogo.page.urls')),
    path('nurseries/', include('catalogo.nurseries.urls')),
    path('property/', include('catalogo.property.urls')),
    path('empiricalknowledge/', include('catalogo.empirical_knowledge.urls')),
    path('auth/', include('catalogo.auth.urls')),
    path('utils/', include('catalogo.utils.urls'))
]