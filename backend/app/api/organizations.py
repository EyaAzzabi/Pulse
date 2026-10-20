from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_membership, require_role
from app.db.session import get_db
from app.models.organization import BusinessProfile, Organization
from app.models.user import Membership, User
from app.schemas.organization import (
    BusinessProfileOut,
    BusinessProfileUpdate,
    MemberOut,
    OrganizationOut,
    OrganizationUpdate,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("", response_model=list[OrganizationOut])
def list_organizations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memberships = db.query(Membership).filter(Membership.user_id == user.id).all()
    results = []
    for m in memberships:
        org = db.get(Organization, m.organization_id)
        if org:
            results.append(OrganizationOut(role=m.role, **{k: getattr(org, k) for k in
                ["id", "name", "industry", "country", "currency", "company_size", "timezone", "is_demo"]}))
    return results


@router.get("/{organization_id}", response_model=OrganizationOut)
def get_organization(organization_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    membership = require_membership(organization_id, user, db)
    org = db.get(Organization, organization_id)
    if not org:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization not found")
    return OrganizationOut(role=membership.role, **{k: getattr(org, k) for k in
        ["id", "name", "industry", "country", "currency", "company_size", "timezone", "is_demo"]})


@router.patch("/{organization_id}", response_model=OrganizationOut)
def update_organization(
    organization_id: str,
    payload: OrganizationUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = require_role(organization_id, user, db, "OWNER")
    org = db.get(Organization, organization_id)
    if not org:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(org, field, value)
    db.commit()
    return OrganizationOut(role=membership.role, **{k: getattr(org, k) for k in
        ["id", "name", "industry", "country", "currency", "company_size", "timezone", "is_demo"]})


@router.get("/{organization_id}/members", response_model=list[MemberOut])
def list_members(organization_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_membership(organization_id, user, db)
    memberships = db.query(Membership).filter(Membership.organization_id == organization_id).all()
    out = []
    for m in memberships:
        member_user = db.get(User, m.user_id)
        if member_user:
            out.append(MemberOut(user_id=member_user.id, full_name=member_user.full_name, email=member_user.email, role=m.role))
    return out


@router.get("/{organization_id}/business-profile", response_model=BusinessProfileOut)
def get_business_profile(organization_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_membership(organization_id, user, db)
    profile = db.query(BusinessProfile).filter(BusinessProfile.organization_id == organization_id).first()
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Business profile not found")
    return profile


@router.patch("/{organization_id}/business-profile", response_model=BusinessProfileOut)
def update_business_profile(
    organization_id: str,
    payload: BusinessProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(organization_id, user, db, "FINANCE_MANAGER")
    profile = db.query(BusinessProfile).filter(BusinessProfile.organization_id == organization_id).first()
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Business profile not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    return profile
