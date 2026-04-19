from celery import Celery

celery_app = Celery(
    "sentra",
    broker="redis://localhost:6380/0",
    backend="redis://localhost:6380/0",
    include=["app.tasks.pipeline"]
)