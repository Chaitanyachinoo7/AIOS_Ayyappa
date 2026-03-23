from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, db_session, engine
from app.models.event import Event
from app.webhooks.base import safe_json_loads
from app.worker import celery_app


router = APIRouter()


def _ensure_schema() -> None:
    Base.metadata.create_all(bind=engine)


@router.post("")
async def inbound_webhook(request: Request) -> JSONResponse:
    _ensure_schema()

    raw_body = await request.body()
    payload = safe_json_loads(raw_body)

    if settings.telegram_webhook_secret:
        header_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if header_secret != settings.telegram_webhook_secret:
            raise HTTPException(status_code=401, detail="invalid webhook secret")

    headers = {k: v for k, v in request.headers.items()}

    with db_session() as session:
        event = Event(source="telegram", signature_valid=True, headers=headers, payload=payload)
        session.add(event)
        session.flush()
        event_id = str(event.id)

    celery_app.send_task("process_event", args=[event_id])
    return JSONResponse({"ok": True, "event_id": event_id})
