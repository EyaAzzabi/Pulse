from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_authenticated_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.organization import BusinessProfile, OnboardingProgress, Organization
from app.models.user import Membership, User
from app.schemas.auth import (
    LoginRequest,
    MeResponse,
    MembershipOut,
    OtpRequest,
    OtpResponse,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from app.services.otp import OtpCooldown, OtpError, issue_code, verify_code

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/request-otp", response_model=OtpResponse)
def request_otp(payload: OtpRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")
    try:
        delivery = issue_code(db, email)
    except OtpCooldown:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Please wait a minute before requesting a new code")
    except Exception:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Could not send the verification email. Try again shortly.")
    return OtpResponse(delivery=delivery)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")
    try:
        verify_code(db, email, payload.otp_code)
    except OtpError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))

    user = User(email=email, password_hash=hash_password(payload.password), full_name=payload.full_name, account_status="PENDING", email_verified=True)
    db.add(user)
    db.flush()

    org = Organization(name=payload.organization_name)
    db.add(org)
    db.flush()

    db.add(Membership(user_id=user.id, organization_id=org.id, role="OWNER"))
    db.add(BusinessProfile(organization_id=org.id))
    db.add(OnboardingProgress(organization_id=org.id))
    db.commit()

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_authenticated_user), db: Session = Depends(get_db)):
    memberships = db.query(Membership).filter(Membership.user_id == user.id).all()
    out = []
    for m in memberships:
        org = db.get(Organization, m.organization_id)
        out.append(MembershipOut(organization_id=m.organization_id, organization_name=org.name if org else "", role=m.role))
    return MeResponse(user=UserOut.model_validate(user), memberships=out)
