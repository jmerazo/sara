from django.urls import path
from .users import UsersView, UsersStateView, UserPermissionsView, SomeView, RolesView

urlpatterns = [
    path('', UsersView.as_view()),
    path('<int:pk>', UsersView.as_view()),
    path('state/<int:pk>', UsersStateView.as_view()),
    path('modules', UserPermissionsView.as_view()),
    path('roles/', RolesView.as_view()),
]