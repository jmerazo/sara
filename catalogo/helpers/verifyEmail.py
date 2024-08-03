from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from dotenv import load_dotenv
import os

from ..helpers.jwt import verify_jwt
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
    
    user.is_active = True
    user.verificated = True
    user.token = None  # Clear the token after verification
    user.save()

    return Response({'msg': 'Email verified successfully'}, status=status.HTTP_200_OK)

def send_email(subject, body, to):
    try:
        send_mail(
            subject,
            body,
            os.getenv('DEFAULT_FROM_EMAIL'),
            [to],
            fail_silently=False,
        )
        print("Email sent successfully")
    except Exception as e:
        print(f"An error occurred: {e}")
