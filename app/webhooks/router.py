from __future__ import annotations

from fastapi import APIRouter

from app.webhooks.whatsapp import router as whatsapp_router
from app.webhooks.telegram import router as telegram_router


router = APIRouter()
router.include_router(whatsapp_router, prefix="/whatsapp", tags=["whatsapp"])
router.include_router(telegram_router, prefix="/telegram", tags=["telegram"])

