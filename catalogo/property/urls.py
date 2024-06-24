from django.urls import path
from .property import PropertyView, UserPropertyFileView, PropertyUserIdView

urlpatterns = [
    # PAGE
    path('', PropertyView.as_view()), # Retorna el contenido de la página -- http://localhost:8000/api/page/content
    path('<int:pk>', PropertyView.as_view()),
    path('search/<int:pk>', PropertyUserIdView.as_view()),
    path('users', UserPropertyFileView.as_view()),
    path('users/<int:pk>', UserPropertyFileView.as_view())
]