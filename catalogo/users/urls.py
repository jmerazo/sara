from django.urls import path
from .users import UsersView, UsersStateView, UserPermissionsView, SomeView

urlpatterns = [
    path('', UsersView.as_view()),
    path('<int:pk>', UsersView.as_view()),
    path('state/<int:pk>', UsersStateView.as_view()),
    path('modules', UserPermissionsView.as_view()),
]