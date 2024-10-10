from django.urls import path
from .utils import SisaView
from ..helpers.Email import EmailService, EmailContactService

urlpatterns = [
    path('sisa/', SisaView.as_view()),
    path('send-email/', EmailService.as_view()),
    path('contact/send-email/', EmailContactService.as_view())
]