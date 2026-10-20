"""Provision an administrator locally: python scripts/create_admin.py email@example.com

No public endpoint can grant platform administrator privileges.
"""
import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import TypeAdapter, EmailStr
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User
from app import models  # noqa: F401


def main():
    parser = argparse.ArgumentParser(description="Create a PULSE platform administrator after running migrations.")
    parser.add_argument("email")
    parser.add_argument("--name", default="Pulse Administrator")
    args = parser.parse_args()
    email = str(TypeAdapter(EmailStr).validate_python(args.email)).lower()
    with SessionLocal() as db:
        if db.query(User).filter(User.email == email).first():
            parser.error("This account already exists. Choose a dedicated administrator email.")
        password = getpass.getpass("Administrator password (12 characters minimum): ")
        if len(password) < 12 or len(password.encode("utf-8")) > 72:
            parser.error("Use at least 12 characters and at most 72 UTF-8 bytes.")
        if password != getpass.getpass("Confirm password: "):
            parser.error("Passwords do not match.")
        db.add(User(email=email, full_name=args.name, password_hash=hash_password(password), is_admin=True, account_status="APPROVED"))
        db.commit()
    print("Administrator created. Sign in through /login, then open /admin.")


if __name__ == "__main__":
    main()
