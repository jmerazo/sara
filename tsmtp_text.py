# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def send_email():
    try:
        smtp_server = "sara.corpoamazonia.gov.co"
        port = 465  # o 587 si usas TLS
        sender_email = "support@sara.corpoamazonia.gov.co"
        password = "Sara2024*"
        receiver_email = "sheesarte@gmail.com"

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = Header("Asunto de prueba con", "utf-8")

        body = "Este es un correo de prueba con caracteres especiales"
        message.attach(MIMEText(body.encode('utf-8'), 'plain', 'utf-8'))

        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        
        print("Correo enviado exitosamente")
    except UnicodeEncodeError as e:
        print(f"Error de codificación Unicode: {e}")
    except smtplib.SMTPException as e:
        print(f"Error SMTP: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

send_email()