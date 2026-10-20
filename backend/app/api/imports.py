import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.services.notifications import notify
from app.services.tabular_import import (
    ImportSourceError,
    fetch_google_sheet,
    import_table,
    preview,
    read_table,
)

MAX_FILE_BYTES = 5 * 1024 * 1024

router = APIRouter(prefix="/imports", tags=["imports"])


class SheetRequest(BaseModel):
    url: str
    mapping: dict[str, str | None] | None = None


async def _read_upload(file: UploadFile):
    content = await file.read()
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File exceeds the 5 MB limit")
    try:
        return read_table(file.filename or "", content)
    except ImportSourceError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))


def _run_import(db, organization_id, table, mapping):
    try:
        outcome = import_table(db, organization_id, table, mapping)
    except ImportSourceError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    notify(
        db,
        organization_id,
        category="data_import",
        severity="warning" if outcome.errors else "info",
        title=f"Imported {outcome.imported} transaction(s)",
        body=f"{outcome.skipped_duplicates} duplicate(s) skipped, {len(outcome.errors)} row(s) with errors.",
        link="/dashboard",
    )
    db.commit()
    return {"imported": outcome.imported, "skipped_duplicates": outcome.skipped_duplicates, "errors": outcome.errors}


@router.post("/file/preview")
async def preview_file(
    organization_id: str = Query(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(organization_id, user, db, "ACCOUNTANT")
    return preview(await _read_upload(file))


@router.post("/file")
async def import_file(
    organization_id: str = Query(...),
    file: UploadFile = File(...),
    mapping: str = Form(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(organization_id, user, db, "ACCOUNTANT")
    table = await _read_upload(file)
    try:
        parsed = json.loads(mapping)
    except json.JSONDecodeError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid column mapping")
    return _run_import(db, organization_id, table, parsed)


@router.post("/google-sheet/preview")
def preview_sheet(
    payload: SheetRequest,
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(organization_id, user, db, "ACCOUNTANT")
    try:
        return preview(fetch_google_sheet(payload.url))
    except ImportSourceError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))


@router.post("/google-sheet")
def import_sheet(
    payload: SheetRequest,
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(organization_id, user, db, "ACCOUNTANT")
    try:
        table = fetch_google_sheet(payload.url)
    except ImportSourceError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    return _run_import(db, organization_id, table, payload.mapping or {})
