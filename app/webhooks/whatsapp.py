from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse

from app.config import settings
from app.database import Base, db_session, engine
from app.models.event import Event
from app.webhooks.base import safe_json_loads, verify_hmac_sha256
from app.worker import celery_app


router = APIRouter()


def _ensure_schema() -> None:
    Base.metadata.create_all(bind=engine)


@router.get("")
async def verify_webhook(request: Request) -> PlainTextResponse:
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token and token == (settings.whatsapp_verify_token or ""):
        return PlainTextResponse(content=challenge or "")
    raise HTTPException(status_code=403, detail="verification failed")


@router.post("")
async def inbound_webhook(request: Request) -> dict:
    _ensure_schema()

    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    if not settings.whatsapp_app_secret:
        raise HTTPException(status_code=500, detail="WHATSAPP_APP_SECRET not configured")

    if not verify_hmac_sha256(secret=settings.whatsapp_app_secret, body=raw_body, signature_header=signature):
        raise HTTPException(status_code=401, detail="invalid signature")

    payload = safe_json_loads(raw_body)
    headers = {k: v for k, v in request.headers.items()}

    with db_session() as session:
        event = Event(source="whatsapp", signature_valid=True, headers=headers, payload=payload)
        session.add(event)
        session.flush()
        event_id = str(event.id)

    celery_app.send_task("process_event", args=[event_id])
    return {"ok": True, "event_id": event_id}

