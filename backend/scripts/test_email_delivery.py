"""Send a real signup code and verify the code received in the recipient's inbox.

Usage: python scripts/test_email_delivery.py recipient@example.com
       python scripts/test_email_delivery.py recipient@example.com --send-only
"""
import argparse
import getpass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import EmailStr, TypeAdapter
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.services.email import smtp_configured
from app.services.otp import issue_code, verify_code


def main():
    parser = argparse.ArgumentParser(description="Send and optionally verify a real PULSE OTP email.")
    parser.add_argument("email")
    parser.add_argument("--send-only", action="store_true")
    args = parser.parse_args()
    email = str(TypeAdapter(EmailStr).validate_python(args.email)).lower()
    settings = get_settings()
    if not smtp_configured() and not (settings.n8n_otp_webhook_url and settings.n8n_webhook_secret):
        parser.exit(1, "No email channel configured. Fill SMTP_PASSWORD or configure n8n in backend/.env.\n")
    settings.otp_allow_server_log = False
    with SessionLocal() as db:
        try:
            delivery = issue_code(db, email)
        except Exception as exc:
            parser.exit(1, f"Email submission failed ({type(exc).__name__}). Check the email configuration.\n")
        if delivery != "email":
            parser.exit(1, "Email was not submitted.\n")
        print("Code accepted by the email service. Check the inbox and spam folder.")
        if not args.send_only:
            code = getpass.getpass("Code received by email: ").strip()
            try:
                verify_code(db, email, code)
            except Exception:
                parser.exit(1, "Code verification failed.\n")
            print("Inbox receipt and code verification confirmed.")


if __name__ == "__main__":
    main()
