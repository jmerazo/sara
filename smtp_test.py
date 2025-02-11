import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

def send_test_email(use_ssl=False):
    smtp_server = os.getenv('EMAIL_HOST')
    smtp_port = int(os.getenv('EMAIL_PORT'))
    smtp_user = os.getenv('EMAIL_HOST_USER')
    smtp_password = os.getenv('EMAIL_HOST_PASSWORD')
    from_email = os.getenv('DEFAULT_FROM_EMAIL')
    to_email = "jmerazo96@gmail.com"
    subject = "TEST"

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    body = "Este es un correo de prueba."
    msg.attach(MIMEText(body, 'plain'))

    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Correo enviado exitosamente")
    except Exception as e:
        print(f"Error al enviar correo: {e}")

# Probar con SSL
send_test_email(use_ssl=False)
# Probar sin SSL
send_test_email(use_ssl=True)