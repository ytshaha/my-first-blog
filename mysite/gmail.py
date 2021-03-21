
from mysite.Google import Create_Service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings
import os

GMAIL_API_CREDENTIAL_DIRS = getattr(settings, 'GMAIL_API_CREDENTIAL_DIRS', None)
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']

service = Create_Service(GMAIL_API_CREDENTIAL_DIRS, API_NAME, API_VERSION, SCOPES)

def send_email(emailMsg, to, subject):
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = to
    mimeMessage['subject'] = subject
    mimeMessage.attach(MIMEText(emailMsg, 'plain'))
    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

    message = service.users().messages().send(userId='me', body={'raw':raw_string}).execute()
    print(message)