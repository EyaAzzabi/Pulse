from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_membership
from app.db.session import get_db
from app.models.conversation import Notification
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def list_notifications(
    organization_id: str = Query(...),
    unread_only: bool = Query(False),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    query = db.query(Notification).filter(Notification.organization_id == organization_id)
    if unread_only:
        query = query.filter(Notification.read == False)  # noqa: E712
    notifications = query.order_by(Notification.created_at.desc()).limit(100).all()
    return [
        {
            "id": n.id,
            "category": n.category,
            "severity": n.severity,
            "title": n.title,
            "body": n.body,
            "link": n.link,
            "read": n.read,
            "created_at": n.created_at,
        }
        for n in notifications
    ]


@router.get("/unread-count")
def unread_count(
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    count = (
        db.query(Notification)
        .filter(Notification.organization_id == organization_id, Notification.read == False)  # noqa: E712
        .count()
    )
    return {"unread": count}


@router.post("/read-all")
def mark_all_read(
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    updated = (
        db.query(Notification)
        .filter(Notification.organization_id == organization_id, Notification.read == False)  # noqa: E712
        .update({"read": True})
    )
    db.commit()
    return {"marked_read": updated}


@router.patch("/{notification_id}")
def update_notification(
    notification_id: str,
    organization_id: str = Query(...),
    read: bool = Query(True),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    notification = db.get(Notification, notification_id)
    if not notification or notification.organization_id != organization_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
    notification.read = read
    db.commit()
    return {"id": notification.id, "read": notification.read}
