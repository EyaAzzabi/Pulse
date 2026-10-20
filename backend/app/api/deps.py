from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import Membership, User

ROLE_RANK = {"VIEWER": 0, "ACCOUNTANT": 1, "FINANCE_MANAGER": 2, "OWNER": 3}


def get_authenticated_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing or invalid authorization header")
    token = authorization.split(" ", 1)[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    user = db.get(User, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")
    return user


def get_current_user(user: User = Depends(get_authenticated_user)) -> User:
    if user.account_status != "APPROVED":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account approval required")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Administrator access required")
    return user


def require_membership(organization_id: str, user: User, db: Session) -> Membership:
    membership = (
        db.query(Membership)
        .filter(Membership.organization_id == organization_id, Membership.user_id == user.id)
        .first()
    )
    if not membership:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not a member of this organization")
    return membership


def require_role(organization_id: str, user: User, db: Session, minimum_role: str) -> Membership:
    membership = require_membership(organization_id, user, db)
    if ROLE_RANK.get(membership.role, -1) < ROLE_RANK.get(minimum_role, 99):
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"Requires at least role {minimum_role}")
    return membership
