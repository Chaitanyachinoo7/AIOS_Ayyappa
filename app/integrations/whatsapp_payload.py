from __future__ import annotations


def extract_whatsapp_text(payload: dict) -> tuple[str | None, str | None]:
    try:
        entries = payload.get("entry") or []
        for entry in entries:
            changes = entry.get("changes") or []
            for change in changes:
                value = change.get("value") or {}
                messages = value.get("messages") or []
                for msg in messages:
                    from_number = msg.get("from")
                    text = (msg.get("text") or {}).get("body")
                    if from_number and text:
                        return from_number, text
    except Exception:
        return None, None

    return None, None

