from django.urls import path
from .utils import SisaView

urlpatterns = [
    path('sisa/', SisaView.as_view()),
]