from functools import wraps
from django.http import JsonResponse
from firebase_admin import auth

def firebase_token_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            id_token = auth_header.split(' ').pop()
            try:
                decoded_token = auth.verify_id_token(id_token)
                request.user = decoded_token
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=401)
        else:
            return JsonResponse({'error': 'Authorization header is missing'}, status=401)

        return view_func(request, *args, **kwargs)
    return _wrapped_view