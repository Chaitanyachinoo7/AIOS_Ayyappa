from __future__ import annotations

from app.agents.lightweight import run_lightweight_agent
from app.integrations.whatsapp_client import WhatsAppClient
from app.integrations.whatsapp_payload import extract_whatsapp_text
from app.integrations.telegram_client import TelegramClient
from app.integrations.telegram_payload import extract_telegram_text
from app.models.event import Event


def dispatch_whatsapp_message(event: Event) -> dict:
    from_number, text = extract_whatsapp_text(event.payload)
    output = run_lightweight_agent(event, text)

    if from_number:
        client = WhatsAppClient()
        if client.is_configured() and output.get("reply"):
            client.send_text(to=from_number, text=output["reply"])

    return output


def dispatch_telegram_message(event: Event) -> dict:
    chat_id, text = extract_telegram_text(event.payload)
    output = run_lightweight_agent(event, text)

    if chat_id:
        client = TelegramClient()
        if client.is_configured() and output.get("reply"):
            client.send_text(chat_id=chat_id, text=output["reply"])

    return output

