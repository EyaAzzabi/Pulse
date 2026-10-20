"""Email one-time codes for signup. Codes are stored only as an HMAC, expire
after 10 minutes, allow 5 attempts, and are single-use."""
import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.otp import EmailOtp
from app.services.email import EmailNotConfigured, send_email

logger = logging.getLogger(__name__)

CODE_TTL = timedelta(minutes=10)
RESEND_COOLDOWN = timedelta(seconds=60)
MAX_ATTEMPTS = 5


class OtpError(Exception):
    pass


class OtpCooldown(Exception):
    pass


def generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _hash(email: str, code: str) -> str:
    key = get_settings().jwt_secret.encode()
    return hmac.new(key, f"{email.lower()}:{code}".encode(), hashlib.sha256).hexdigest()


def issue_code(db: Session, email: str) -> str:
    """Creates a code, invalidates earlier ones, and delivers it. Returns
    "email" when sent, or "server_log" when no SMTP server is configured."""
    email = email.lower()
    now = datetime.utcnow()
    latest = (
        db.query(EmailOtp)
        .filter(EmailOtp.email == email, EmailOtp.consumed == False)  # noqa: E712
        .order_by(EmailOtp.created_at.desc())
        .first()
    )
    if latest and now - latest.created_at < RESEND_COOLDOWN:
        raise OtpCooldown()

    db.query(EmailOtp).filter(EmailOtp.email == email, EmailOtp.consumed == False).update(  # noqa: E712
        {"consumed": True}
    )
    code = generate_code()
    db.add(EmailOtp(email=email, code_hash=_hash(email, code), expires_at=now + CODE_TTL))
    db.commit()

    text = (
        f"Your Pulse AI verification code is {code}.\n\n"
        "It expires in 10 minutes. If you didn't request it, you can ignore this email."
    )
    html = f"""
    <div style="font-family:Inter,Arial,sans-serif;max-width:480px;margin:auto;padding:32px;color:#0f172a">
      <h2 style="margin:0 0 8px;color:#1e3a8a">Verify your email</h2>
      <p style="color:#64748b;margin:0 0 24px">Enter this code in Pulse AI to finish creating your account.</p>
      <div style="font-size:32px;letter-spacing:8px;font-weight:700;background:#f1f5f9;border-radius:12px;
                  padding:16px;text-align:center">{code}</div>
      <p style="color:#64748b;font-size:13px;margin-top:24px">The code expires in 10 minutes. If you didn't
      request it, you can ignore this email.</p>
    </div>"""
    try:
        send_email(email, "Your Pulse AI verification code", text, html)
        return "email"
    except EmailNotConfigured:
        logger.warning("SMTP not configured. Verification code for %s: %s", email, code)
        return "server_log"


def verify_code(db: Session, email: str, code: str) -> None:
    email = email.lower()
    otp = (
        db.query(EmailOtp)
        .filter(EmailOtp.email == email, EmailOtp.consumed == False)  # noqa: E712
        .order_by(EmailOtp.created_at.desc())
        .first()
    )
    if not otp or otp.expires_at < datetime.utcnow() or otp.attempts >= MAX_ATTEMPTS:
        raise OtpError("This code has expired. Request a new one.")
    if not hmac.compare_digest(otp.code_hash, _hash(email, code)):
        otp.attempts += 1
        db.commit()
        remaining = MAX_ATTEMPTS - otp.attempts
        raise OtpError(f"Incorrect code. {remaining} attempt(s) left." if remaining else "Too many attempts. Request a new code.")
    otp.consumed = True
    db.commit()
