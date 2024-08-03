from django.urls import path
from .page import PageView, UpdateCountVisitsView, TopSpeciesView, PagesView, SectionView

urlpatterns = [
    # PAGE
    path('content', PageView.as_view()), # Retorna el contenido de la página -- http://localhost:8000/api/page/content
    path('content/<int:pk>', PageView.as_view()), # Permite listar, editar o eliminar un contenido -- http://localhost:8000/api/page/content/2
    path('count/<int:code>', UpdateCountVisitsView.as_view()), # Incrementa el contador de una especie forestal -- http://localhost:8000/api/page/count/789
    path('top_species', TopSpeciesView.as_view()), # Retorna las 4 especies mas consultadas en el catálogo -- http://localhost:8000/api/page/top_species

    path('', PagesView.as_view()),
    path('<int:pk>', PagesView.as_view()),
    path('section', SectionView.as_view()),
    path('section/<int:pk>', SectionView.as_view()),
]