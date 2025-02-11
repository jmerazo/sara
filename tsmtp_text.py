import smtplib
from email.mime.text import MIMEText

try:
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'apps@corpoamazonia.gov.co'
    smtp_password = 'dxfs uoio tohn kjvw'

    msg = MIMEText("Este es un correo de prueba desde smtplib.")
    msg['Subject'] = 'Prueba SMTP'
    msg['From'] = smtp_user
    msg['To'] = 'jmerazo96@gmail.com'

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Inicia TLS
    server.login(smtp_user, smtp_password)
    server.sendmail(smtp_user, 'jmerazo96@gmail.com', msg.as_string())
    server.quit()
    print("Correo enviado exitosamente con smtplib.")
except Exception as e:
    print(f"Error al enviar correo con smtplib: {e}")
