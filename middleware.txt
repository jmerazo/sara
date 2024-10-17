from firebase_admin import auth
from django.contrib.auth import get_user_model
from django.conf import settings
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
        return (
            any(path.startswith(prefix) for prefix in self.excluded_prefixes) or
            any(path == excluded for excluded in self.excluded_paths)
        )

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not self.is_path_excluded(request.path_info):
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if not auth_header:
                # No interrumpimos el flujo, permitimos que la vista maneje la autenticación
                return

            try:
                # Asumimos que el header es "Bearer <token>"
                token = auth_header.split()[1]
                decoded_token = auth.verify_id_token(token)
                email = decoded_token.get('email')

                User = get_user_model()
                user = User.objects.get(email=email)
                request.user = user
            except Exception:
                # No interrumpimos el flujo, permitimos que la vista maneje la autenticación
                pass