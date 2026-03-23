from __future__ import annotations

from app.workflows.engine import Node


def _collect(_: dict) -> dict:
    return {"items": ["system healthy"]}


def _summarize(data: dict) -> dict:
    items = data.get("items", [])
    return {"summary": " | ".join(items) if items else "no items"}


nodes = [
    Node(name="collect", fn=_collect),
    Node(name="summarize", fn=_summarize, deps=("collect",)),
]

