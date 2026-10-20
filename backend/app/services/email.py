import logging
import smtplib
from email.message import EmailMessage

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EmailNotConfigured(Exception):
    pass


def smtp_configured() -> bool:
    s = get_settings()
    return bool(s.smtp_host and s.smtp_user and s.smtp_password)


def send_email(to: str, subject: str, text: str, html: str | None = None) -> None:
    """Sends through the configured SMTP server. Raises EmailNotConfigured when
    no server is set up, and lets SMTP errors propagate so callers never report
    an email as sent when it wasn't."""
    s = get_settings()
    if not smtp_configured():
        raise EmailNotConfigured()

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = s.smtp_from or s.smtp_user
    msg["To"] = to
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")

    with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=15) as server:
        server.starttls()
        server.login(s.smtp_user, s.smtp_password)
        server.send_message(msg)
