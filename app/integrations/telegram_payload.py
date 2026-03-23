from __future__ import annotations


def extract_telegram_text(payload: dict) -> tuple[int | str | None, str | None]:
    """Return (chat_id, text) from webhook payload."""
    if not payload:
        return None, None

    message = payload.get("message") or payload.get("edited_message")
    if not isinstance(message, dict):
        return None, None

    chat = message.get("chat")
    chat_id = None
    if isinstance(chat, dict):
        chat_id = chat.get("id")

    text = message.get("text")
    if text is None and "caption" in message:
        text = message.get("caption")

    return chat_id, text
