from . import *
import os
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

SENDER_EMAIL_ADDRESS = os.environ.get("S2N2S2-EMAIL")
SENDER_EMAIL_KEY = os.environ.get("S2N2S2-EMAIL-KEY")


def send_email(email_address, subject, body, attachements=[]):
    """
    Sends an email.
    Args:
        email_address: Receiver's email address
        subject: Subject of the email
        body: Body of the email
        attachements : array of dict's containing path of the file to be attached and name to be given of the attached file.
    """
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    context = ssl.create_default_context()

    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = SENDER_EMAIL_ADDRESS
    message["To"] = email_address
    body_part = MIMEText(body)
    message.attach(body_part)

    for attachement in attachements:
        with open(attachement["path"], "rb") as file:
            message.attach(MIMEApplication(file.read(), Name=attachement["name"]))

    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(SENDER_EMAIL_ADDRESS, SENDER_EMAIL_KEY)
        server.send_message(message)