import os
import json
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from dotenv import load_dotenv

load_dotenv()

@csrf_exempt
@require_POST
def verify_recaptcha(request):
    try:
        data = json.loads(request.body)
        recaptcha_response = data.get('token')
        
        values = {
            'secret': os.getenv('RECAPTCHA_PRIVATE_KEY'),
            'response': recaptcha_response
        }
        
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=values)
        result = r.json()
        
        if result['success']:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'reCAPTCHA verification failed'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})