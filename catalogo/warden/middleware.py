import pytz, time
from datetime import timedelta
from firebase_admin import auth
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from .csrfMiddleware import CsrfExemptAPIMiddleware

def get_user(request):
    User = get_user_model()
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header:
        return None

    try:
        # Asumimos que el header es "Bearer <token>"
        token = auth_header.split()[1]
        decoded_token = auth.verify_id_token(token)
        email = decoded_token.get('email')
        user = User.objects.get(email=email)
        return user
    except Exception:
        return None

import logging

logger = logging.getLogger(__name__)

class FirebaseAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.excluded_paths = getattr(settings, 'EXCLUDED_PATHS', [])
        self.excluded_prefixes = [
            '/api/images/',
            '/api/species/search/code/',
            '/api/species/search/family/',
            '/api/users/verify-email/',
        ]

    def is_path_excluded(self, path):
        logger.debug(f"Verificando si la ruta '{path}' está excluida.")
        return (
            any(path.startswith(prefix) for prefix in self.excluded_prefixes) or
            any(path == excluded for excluded in self.excluded_paths)
        )

    def __call__(self, request):
        if not self.is_path_excluded(request.path_info):
            logger.debug(f"Validando token para la ruta '{request.path_info}'.")
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if not auth_header:
                logger.warning("Encabezado de autorización faltante.")
                return JsonResponse(
                    {"detail": "Authorization header is missing."},
                    status=403
                )
            try:
                token = auth_header.split()[1]
                logger.debug(f"Token recibido: {token[:10]}...")
                decoded_token = auth.verify_id_token(token, check_revoked=True, clock_skew_seconds=5)
                logger.debug(f"Token decodificado: {decoded_token}")
                email = decoded_token.get('email')
                if not email:
                    raise ValueError("El token no contiene un correo electrónico.")
                
                current_time = int(time.time())
                logger.debug(f"Tiempo actual del servidor: {current_time}")
                logger.debug(f"Tiempo 'nbf' del token: {decoded_token.get('nbf')}")
                logger.debug(f"Tiempo 'exp' del token: {decoded_token.get('exp')}")
                
                User = get_user_model()
                user = User.objects.get(email=email)
                request.user = user
            except Exception as e:
                logger.error(f"Error durante la autenticación: {str(e)}")
                return JsonResponse({"detail": "Authentication failed."}, status=403)
        
        response = self.get_response(request)
        return response