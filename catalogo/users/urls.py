from django.urls import path
from .users import UsersView, UsersStateView, UserPermissionsView, SomeView, RolesView, UserRegisterView
from ..helpers.Email import verifyEmail

urlpatterns = [
    path('', UsersView.as_view()),
    path('register/', UserRegisterView.as_view()),
    path('<int:pk>', UsersView.as_view()),
    path('state/<int:pk>', UsersStateView.as_view()),
    path('modules', UserPermissionsView.as_view()),
    path('roles/', RolesView.as_view()),
    path('verify-email/<str:token>', verifyEmail),
]