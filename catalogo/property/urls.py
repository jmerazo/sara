from django.urls import path
from .property import PropertyView, UserPropertyFileView, PropertyUserIdView, MonitoringPropertyView, PropertyRecordSearchView, SpeciesRecordView

urlpatterns = [
    # PAGE
    path('', PropertyView.as_view()), # Retorna el contenido de la página -- http://localhost:8000/api/page/content
    path('<int:pk>', PropertyView.as_view()),
    path('search/<int:pk>', PropertyUserIdView.as_view()),
    path('users', UserPropertyFileView.as_view()),
    path('users/<int:pk>', UserPropertyFileView.as_view()),
    path('users/record-search/<int:pk>', PropertyRecordSearchView.as_view()),
    path('users/monitoring', MonitoringPropertyView.as_view()), # Retorna listado de usuarios y meta de monitoreos por especie -- http://localhost:8000/api/property/users/monitoring
    path('users/species', SpeciesRecordView.as_view())
]