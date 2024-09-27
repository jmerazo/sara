from django.utils.deprecation import MiddlewareMixin

class CsrfExemptAPIMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Exime de verificación CSRF las rutas que comienzan con '/api/'
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)