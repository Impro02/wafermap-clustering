# MODULES
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from configs.config import MailingConfig


def send_mail(
    host: str, port: int, sender: str, receiver: str, subject: str, msg_html: str
):

    message = MIMEMultipart("alternative")

    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = subject
    message.attach(MIMEText(msg_html, "html"))
    # Create secure connection with server and send email
    # context = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.sendmail(sender, receiver, message.as_string())


def send_mail_error(klarf: str, error_path: str, config: MailingConfig) -> str:
    message_error = f"{klarf=} processing failed, moved to {error_path}"

    html = f"""\
        <html>
            <body>
                <p>{message_error}</p>
            </body>
        </html>
    """

    send_mail(
        host=config.host,
        port=config.port,
        sender=config.sender,
        receiver=config.receiver,
        subject=f"Clustering - Error on {klarf}",
        msg_html=html,
    )

    return message_error
