"""Email sending service using Gmail SMTP."""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

from app.agent.email_agent import EmailDigest
from app.database.repository import validate_email_address, validate_gmail_address

load_dotenv()

GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587


def send_email_digest(
    recipient_email: str,
    digest: EmailDigest,
    sender_email: str | None = None,
    app_password: str | None = None,
) -> None:
    """Send a rendered digest email through Gmail SMTP."""

    sender = sender_email or os.getenv("GMAIL_ADDRESS")
    password = app_password or os.getenv("GMAIL_APP_PASSWORD")
    if not sender or not password:
        raise RuntimeError("Missing GMAIL_ADDRESS or GMAIL_APP_PASSWORD in .env.")

    sender = validate_gmail_address(sender)
    recipient_email = validate_email_address(recipient_email)

    message = EmailMessage()
    message["Subject"] = digest.subject
    message["From"] = sender
    message["To"] = recipient_email
    message.set_content(digest.text_body)
    message.add_alternative(digest.html_body, subtype="html")

    with smtplib.SMTP(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        smtp.send_message(message)
