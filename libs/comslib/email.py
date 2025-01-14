from . import *
import os
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

SENDER_EMAIL_ADDRESS = os.environ.get("S2N2S2EMAIL")
SENDER_EMAIL_KEY = os.environ.get("S2N2S2EMAILKEY")


def send_email(
    email_address, subject, body, attachements=[], cc_addresses=[], is_html=False
) -> bool:
    """
    Sends an email.
    Args:
        email_address: Receiver's email address
        subject: Subject of the email
        body: Body of the email
        attachements : array of dict's containing path of the file to be attached and name to be given of the attached file.
        cc_addresses: array of CC email addresses.
    """
    if is_valid_email(email_address):
        smtp_server = "smtp.gmail.com"
        smtp_port = 465
        context = ssl.create_default_context()

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL_ADDRESS
        message["To"] = email_address

        if cc_addresses:
            message["Cc"] = ", ".join(cc_addresses)

        if is_html:
            body_part = MIMEText(body, "html")
            message.attach(body_part)
        else:
            body_part = MIMEText(body, "plain")
            message.attach(body_part)

        for attachement in attachements:
            with open(attachement["path"], "rb") as file:
                message.attach(MIMEApplication(file.read(), Name=attachement["name"]))

        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(SENDER_EMAIL_ADDRESS, SENDER_EMAIL_KEY)
            # server.sendmail(SENDER_EMAIL_ADDRESS, email_address, message.as_string())
            server.send_message(
                message
            )  # TODO - See if I can get any confirmation on successful email dispatch here
            server.quit()

        log_debug(f"Email to <{email_address}> successful.")
        return True
    else:
        log_warning(f"<{email_address}> is an invalid email address.")
        return False
