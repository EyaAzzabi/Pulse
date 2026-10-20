from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.conversation import Notification

DEDUPE_WINDOW = timedelta(days=7)


def notify(
    db: Session,
    organization_id: str,
    category: str,
    title: str,
    body: str = "",
    severity: str = "info",
    link: str = "",
    dedupe: bool = False,
) -> Notification | None:
    """Creates an in-app notification. With dedupe=True, an identical title in
    the same category within the last 7 days is not repeated (used for alerts
    that recompute often, like forecast shortfalls). Caller commits."""
    if dedupe:
        exists = (
            db.query(Notification.id)
            .filter(
                Notification.organization_id == organization_id,
                Notification.category == category,
                Notification.title == title,
                Notification.created_at >= datetime.utcnow() - DEDUPE_WINDOW,
            )
            .first()
        )
        if exists:
            return None
    n = Notification(
        organization_id=organization_id,
        category=category,
        severity=severity,
        title=title,
        body=body,
        link=link,
    )
    db.add(n)
    return n
