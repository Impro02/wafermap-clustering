# MODULES
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_mail(sender: str, receiver: str, subject: str, msg_html: str):

    message = MIMEMultipart("alternative")

    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = subject
    message.attach(MIMEText(msg_html, "html"))
    # Create secure connection with server and send email
    # context = ssl.create_default_context()
    with smtplib.SMTP("c1mailhub0.cro.st.com", 25) as server:
        server.sendmail(sender, receiver, message.as_string())
