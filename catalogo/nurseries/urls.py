from django.urls import path
from .nurseries import NurseriesView, NurseriesAdminView

urlpatterns = [
    path('', NurseriesView.as_view()),
    path('<int:pk>', NurseriesView.as_view()),
    path('admin', NurseriesAdminView.as_view()),
    path('admin/<int:pk>', NurseriesAdminView.as_view()),
]