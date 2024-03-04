from django.urls import path
from .empiricalknowledge import EmpiricalKnowledgeView

urlpatterns = [
    path('', EmpiricalKnowledgeView.as_view()), # (PROTECT) Lista los individuos evaluados totales -- http://localhost:8000/api/candidates/trees
    path('<str:pk>', EmpiricalKnowledgeView.as_view()), # (PROTECT) Lista los individuos evaluados totales -- http://localhost:8000/api/candidates/trees
]