from django.urls import path
from .users import UsersView, UsersStateView

urlpatterns = [
    path('users/', UsersView.as_view()),
    path('users/<int:pk>', UsersView.as_view()),
    path('users/state/<int:pk>', UsersStateView.as_view())
]