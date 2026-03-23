from __future__ import annotations

import httpx

from app.config import settings


class TelegramClient:
    def __init__(self) -> None:
        self._bot_token = settings.telegram_bot_token

    def is_configured(self) -> bool:
        return bool(self._bot_token)

    def send_text(self, *, chat_id: int | str, text: str) -> dict:
        if not self.is_configured():
            raise RuntimeError("Telegram client not configured")

        url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "MarkdownV2",
        }

        with httpx.Client(timeout=20) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
