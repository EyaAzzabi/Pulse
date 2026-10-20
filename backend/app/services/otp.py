"""Email one-time codes for signup. Codes are stored only as an HMAC, expire
after 10 minutes, allow 5 attempts, and are single-use."""
import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timedelta

import httpx
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.otp import EmailOtp
from app.services.email import EmailNotConfigured, send_email, smtp_configured

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
    """Creates a code and submits it through n8n or SMTP.

    Server-log delivery requires explicit development/test opt-in. A failed
    submission removes the unseen code instead of locking out the next attempt.
    """
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
    otp = EmailOtp(email=email, code_hash=_hash(email, code), expires_at=now + CODE_TTL)
    db.add(otp)
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
        return _deliver(email, code, text, html)
    except Exception:
        # A failed delivery must not leave a valid unseen code or a resend lockout.
        db.delete(otp)
        db.commit()
        raise


def _send_via_n8n(email: str, code: str, html: str) -> None:
    s = get_settings()
    if not s.n8n_webhook_secret:
        raise EmailNotConfigured("n8n Header Auth secret is required")
    headers = {"X-Webhook-Secret": s.n8n_webhook_secret} if s.n8n_webhook_secret else {}
    response = httpx.post(
        s.n8n_otp_webhook_url,
        json={"email": email, "code": code, "subject": "Your Pulse AI verification code", "html": html},
        headers=headers,
        timeout=15.0,
    )
    response.raise_for_status()
    result = response.json()
    # Accept the explicit workflow receipt, or Gmail's legacy last-node result.
    if not isinstance(result, dict) or not (result.get("id") or (result.get("sent") is True and result.get("message_id"))):
        raise RuntimeError("n8n did not confirm email submission")


def _deliver(email: str, code: str, text: str, html: str) -> str:
    """n8n first (when configured), then SMTP, then the server log. A configured
    channel that fails never degrades silently to the log: with no other channel
    left it raises, so the API returns an error instead of a code nobody gets."""
    if get_settings().n8n_otp_webhook_url:
        try:
            _send_via_n8n(email, code, html)
            return "email"
        except Exception:
            logger.warning("n8n verification delivery failed; checking SMTP fallback")
            if not smtp_configured():
                raise
    try:
        send_email(email, "Your Pulse AI verification code", text, html)
        return "email"
    except EmailNotConfigured:
        if not get_settings().otp_allow_server_log or get_settings().environment.lower() not in {"development", "test"}:
            raise
        logger.warning("No email channel configured. Verification code for %s: %s", email, code)
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
