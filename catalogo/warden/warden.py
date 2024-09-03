import jwt
import os
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.urls import resolve
from ..models import Users

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Rutas que no requieren autenticación
        exempt_urls = [
            '/api/auth/login', 
            '/api/register/', 
            '/api/refresh-token/',
            '/api/departments/',
            '/api/cities/',
            '/api/species/',
            '/api/species/families',
            '/api/glossary',
            '/api/nurseries/',
            '/api/page/content',
            '/api/page/top_species',
            '/api/utils/sisa/',
            '/api/monitoring/report/dataFlowerAndFruit',
            '/api/species/report/general',
            '/api/candidates/geolocation'
        ]
        
        if request.path_info.startswith('/api/images/') or request.path_info.startswith('/api/species/search/code/') or request.path_info.startswith('/api/species/search/family/'):
            return self.get_response(request)

        if request.path_info not in exempt_urls:
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if not auth_header:
                return JsonResponse({'error': _('No se proporcionó token de autorización')}, status=401)
            
            try:
                token = auth_header.split()[1]
                payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=[os.getenv('ALGORITHM')])
                
                # Verificar si el usuario existe y está activo
                try:
                    user = Users.objects.get(id=payload['id'])
                    if not user.is_active:
                        return JsonResponse({'error': _('Usuario no activo')}, status=401)
                    request.user = user
                except Users.DoesNotExist:
                    return JsonResponse({'error': _('Usuario no encontrado')}, status=404)
                
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': _('El token ha expirado')}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': _('Token inválido')}, status=401)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        
        response = self.get_response(request)
        return response