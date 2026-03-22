from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sentry_sdk
from sqlalchemy import select

from app.config import settings
from app.database import Base, db_session, engine
from app.models.event import Event, EventStatus
from app.models.result import Result
from app.worker import celery_app


if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn)


def _ensure_schema() -> None:
    Base.metadata.create_all(bind=engine)


@celery_app.task(name="process_event")
def process_event(event_id: str) -> dict:
    _ensure_schema()

    try:
        event_uuid = uuid.UUID(event_id)
    except Exception:
        return {"ok": False, "error": "invalid event_id"}

    with db_session() as session:
        event = session.get(Event, event_uuid)
        if not event:
            return {"ok": False, "error": "event not found"}

        event.status = EventStatus.processing
        session.flush()

    try:
        output = _route_event(event_uuid)
        with db_session() as session:
            event = session.get(Event, event_uuid)
            if event:
                event.status = EventStatus.completed
                event.processed_at = datetime.now(timezone.utc)
                session.add(Result(event_id=event_uuid, kind=output.get("kind", "unknown"), output=output))
        return {"ok": True, "event_id": event_id, "output": output}
    except Exception as e:
        sentry_sdk.capture_exception(e)
        with db_session() as session:
            event = session.get(Event, event_uuid)
            if event:
                event.status = EventStatus.failed
                event.processed_at = datetime.now(timezone.utc)
                event.error = str(e)
        return {"ok": False, "event_id": event_id, "error": str(e)}


def _route_event(event_id: uuid.UUID) -> dict:
    with db_session() as session:
        event = session.get(Event, event_id)
        if not event:
            raise RuntimeError("event not found")

        if event.source == "whatsapp":
            from app.agents.dispatcher import dispatch_whatsapp_message

            return dispatch_whatsapp_message(event)

    return {"kind": "noop", "message": "no handler"}


@celery_app.task(name="run_workflow")
def run_workflow(workflow_name: str, initial_data: dict | None = None) -> dict:
    _ensure_schema()

    from app.workflows.engine import run_workflow

    try:
        output = run_workflow(workflow_name, initial_data or {})
        return {"ok": True, "workflow": workflow_name, "output": output}
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return {"ok": False, "workflow": workflow_name, "error": str(e)}

