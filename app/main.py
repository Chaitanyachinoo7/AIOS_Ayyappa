from __future__ import annotations

import sentry_sdk
from fastapi import FastAPI

from app.config import settings
from app.webhooks.router import router as webhooks_router


if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn)


app = FastAPI(title="AI OS", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"ok": True}


app.include_router(webhooks_router, prefix="/webhooks")

