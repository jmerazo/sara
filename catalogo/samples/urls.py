from django.urls import path
from .samples import SamplesView
from ..reports.samples import SamplesReport

urlpatterns = [
    path('report/general', SamplesReport.as_view()), # Retorna el total de muestras por municipio -- http://localhost:8000/api/samples/report/general
    path('report/data', SamplesView.as_view()), # (PROTECT) Exporta todas las muestras registradas -- http://localhost:8000/api/samples/report/data
]