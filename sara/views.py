from django.http import HttpResponse

def index(request):
    message = 'Conectado a la API Sara de Corpoamazonia'
    return HttpResponse(message)