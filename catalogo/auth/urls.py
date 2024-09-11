from django.urls import path
from .authFirebase import FirebaseLoginView, AuthView
from ..helpers.jwt import verify_token
from ..helpers.recaptcha import verify_recaptcha

urlpatterns = [
    path('login', AuthView.as_view()),
    path('verify-token', verify_token),
    path('verify-recaptcha', verify_recaptcha)
]