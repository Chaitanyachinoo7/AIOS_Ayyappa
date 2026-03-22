from __future__ import annotations

from celery.schedules import crontab

from app.worker import celery_app


celery_app.conf.beat_schedule = {
    "daily-health-check": {
        "task": "run_workflow",
        "schedule": crontab(minute="*/10"),
        "args": ["content.daily_report"],
    }
}

