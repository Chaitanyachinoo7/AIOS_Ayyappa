from __future__ import annotations

from fastapi import APIRouter

from app.webhooks.whatsapp import router as whatsapp_router


router = APIRouter()
router.include_router(whatsapp_router, prefix="/whatsapp", tags=["whatsapp"])

