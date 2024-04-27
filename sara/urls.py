from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from catalogo.auth.auth import CustomTokenObtainPairView
from django.conf import settings
from django.conf.urls.static import static
from . import views

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="SARA API",
      default_version='v1',
      description="Descripción de las rutas y modelos de la api",
    #   terms_of_service="https://www.google.com/policies/terms/",
    #   contact=openapi.Contact(email="contact@snippets.local"),
    #   license=openapi.License(name="BSD License"),
   ),
   public=True,
   
)

urlpatterns = [
   path('', views.index, name='index'),
   path('admin/', admin.site.urls),
   path('api/', include('catalogo.urls')),
   path('api/auth/', include('allauth.urls')),
   path('api/auth/token/', CustomTokenObtainPairView.as_view()),
   path('api/auth/token/refresh/', TokenRefreshView.as_view()),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
   path('api/accounts/google/login/callback/', include('social_django.urls')),
]

# Configurar la ruta estática para las imágenes
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
