from django.urls import path
from .nurseries import NurseriesView

urlpatterns = [
    path('', NurseriesView.as_view()),
    path('<int:pk>', NurseriesView.as_view()),
]