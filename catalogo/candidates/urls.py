from django.urls import path
from .candidates import CandidatesTreesView, GeoCandidateTreesView, AverageCandidateTreesView, CandidatesSpecieUserView, SearchCandidatesSpecieView
from ..helpers.excel_export import ExportCandidateTrees


urlpatterns = [
    path('geolocation', GeoCandidateTreesView.as_view()), # Retorna los individuos con sus coordenadas y datos de ubicación -- http://localhost:8000/api/candidates/geolocation
    path('average', AverageCandidateTreesView.as_view()), # Retorna datos de altura total, comercial, cobertura, altitud para promedios -- http://localhost:8000/api/candidates/average
    path('trees', CandidatesTreesView.as_view()), # (PROTECT) Lista los individuos evaluados totales -- http://localhost:8000/api/candidates/trees
    path('trees/<int:np>', CandidatesTreesView.as_view()), # (PROTECT) Lista los individuos evaluados totales -- http://localhost:8000/api/candidates/trees
    path('export/all', ExportCandidateTrees.as_view()), # (PROTECT) Exporta en excel los individuos evaluados totales -- http://localhost:8000/api/candidates/export/all
    path('user/<int:user_id>', CandidatesSpecieUserView.as_view()),
    path('search/<int:code>', SearchCandidatesSpecieView.as_view())
]