from __future__ import annotations

import httpx

from app.config import settings


class WhatsAppClient:
    def __init__(self) -> None:
        self._phone_number_id = settings.whatsapp_phone_number_id
        self._access_token = settings.whatsapp_access_token

    def is_configured(self) -> bool:
        return bool(self._phone_number_id and self._access_token)

    def send_text(self, *, to: str, text: str) -> dict:
        if not self.is_configured():
            raise RuntimeError("WhatsApp client not configured")

        url = f"https://graph.facebook.com/v20.0/{self._phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }

        headers = {"Authorization": f"Bearer {self._access_token}"}

        with httpx.Client(timeout=20) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()

