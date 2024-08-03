from django.urls import path
from .auth import OAuth2Call
from .authFirebase import firebase_login

urlpatterns = [
    path('callback', OAuth2Call.as_view()), # Retorna los individuos con sus coordenadas y datos de ubicación -- http://localhost:8000/api/candidates/geolocation
    path('login', firebase_login)
]