import asyncio

from celery import Celery

from benchmarks.mail.tasks import send_email_async_task, send_email_sync_task

celery_app = Celery(broker="redis://localhost:6379/0")


@celery_app.task
def send_email_task_sync(name: str, username: str, email: str):
    send_email_sync_task(name, username, email)


@celery_app.task
def send_email_task_async(name: str, username: str, email: str):
    asyncio.run(send_email_async_task(name, username, email))
