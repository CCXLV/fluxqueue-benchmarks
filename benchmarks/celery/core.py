import asyncio

from celery import Celery

from benchmarks.mail.tasks import send_email_task

celery_app = Celery(broker="redis://localhost:6379/0")


@celery_app.task
def celery_send_email_task(name: str, username: str, email: str):
    asyncio.run(send_email_task(name, username, email))
