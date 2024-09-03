from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .jwt import verify_jwt
from ..models import Users

@api_view(['GET'])
def verifyEmail(request, token):
    payload = verify_jwt(token)
    if not payload:
        return Response({'msg': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
    
    email = payload.get('id')
    user = Users.objects.filter(email=email).first()
    
    if not user:
        return Response({'msg': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    user.verificated = True
    user.token = None  # Clear the token after verification
    user.save()

    return Response({'msg': 'Email verified successfully'}, status=status.HTTP_200_OK)

def send_email(subject, body, to_email, html_content=None, attachments=None):
    try:
        msg = EmailMultiAlternatives(subject, body, settings.EMAIL_HOST_USER, [to_email])
        if html_content:
            msg.attach_alternative(html_content, "text/html")
        if attachments:
            for attachment in attachments:
                msg.attach(*attachment)
        msg.send()
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def send_verification_email(user, token):
    verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
    email_context = {
        'first_name': user.first_name,
        'verification_url': verification_url,
    }

    email_body = render_to_string('emailVerification.html', email_context)

    email_subject = 'Sara | Verificación de cuenta'
    
    msg = EmailMultiAlternatives(email_subject, email_body, settings.EMAIL_HOST_USER, [user.email])
    msg.attach_alternative(email_body, "text/html")
    
    # Adjunta la imagen con un CID
    with open('catalogo/helpers/resources/imgs/sara.png', 'rb') as f:
        msg_img = MIMEImage(f.read())
        msg_img.add_header('Content-ID', '<logo>')
        msg.attach(msg_img)

    msg.send()

@method_decorator(csrf_exempt, name='dispatch')
class EmailService(APIView):
    def post(self, request):
        subject = request.data.get('subject')
        body = request.data.get('body')
        from_email = request.data.get('from_email')
        
        if not all([subject, body, from_email]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Dirección de correo de atención al público
        to_email = 'support@sara.corpoamazonia.gov.co'
        
        # Agregar el correo del remitente al cuerpo del mensaje
        full_body = f"Correo del remitente: {from_email}\n\n{body}"
        
        success = send_email(subject, full_body, to_email, from_email)
        
        if success:
            return Response({'message': 'Email sent successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
