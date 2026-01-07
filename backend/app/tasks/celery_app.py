"""
Celery application configuration.
"""

from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "date_concierge",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.intelligence"],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/New_York",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.INTELLIGENCE_JOB_TIMEOUT_SECONDS,
    task_soft_time_limit=settings.INTELLIGENCE_JOB_TIMEOUT_SECONDS - 30,
)

# Periodic tasks configuration (optional)
celery_app.conf.beat_schedule = {
    "refresh-stale-intelligence": {
        "task": "app.tasks.intelligence.refresh_stale_intelligence",
        "schedule": 3600.0,  # Run every hour
    },
}

if __name__ == "__main__":
    celery_app.start()
