from django.urls import path, include
from .views import  GlossaryView, PageView
from .administration.users import UsersView, UsersStateView
from .helpers.locates import DepartmentsView, CitiesView
from .page.general import UpdateCountVisitsView, topSpeciesView


urlpatterns = [
    path('glossary', GlossaryView.as_view()),

    # PAGE
    path('page/content', PageView.as_view(), name='page-list'),
    path('page/content/<int:pk>', PageView.as_view(), name='page-detail'),
    path('page/count/<int:code>', UpdateCountVisitsView.as_view(), name='count-visit'),
    path('page/top_species', topSpeciesView.as_view(), name='top_species'),

    path('users/', UsersView.as_view()),
    path('users/<int:pk>', UsersView.as_view()),
    path('users/state/<int:pk>', UsersStateView.as_view()),

    path('departments/', DepartmentsView.as_view()),
    path('cities/', CitiesView.as_view()),

    # ===========================================================
    path('administrator/', include('catalogo.administration.urls')),
    path('samples/', include('catalogo.samples.urls')),
    path('candidates/', include('catalogo.candidates.urls')),
    path('monitoring/', include('catalogo.monitorings.urls')),
    path('species/', include('catalogo.species.urls')),
]