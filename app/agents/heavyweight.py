from __future__ import annotations

from app.models.event import Event


def run_heavyweight_agent(_: Event) -> dict:
    return {"kind": "agent", "error": "heavyweight agent not wired yet"}

