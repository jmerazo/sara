from functools import wraps
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _

def jwt_auth_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return JsonResponse({'error': _('Autenticación requerida')}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapped_view

def firebase_auth_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user or request.user.is_anonymous:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        return view_func(request, *args, **kwargs)
    return wrapped_view