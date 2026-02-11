import asyncio

from celery import Celery

from benchmarks.tasks import calculate_user_commission, send_email_task

celery_app = Celery(broker="redis://localhost:6379/0")

# Create a single event loop per worker process and reuse it for all async work.
_event_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_event_loop)


@celery_app.task
def celery_send_email_task(name: str, username: str, email: str):
    _event_loop.run_until_complete(send_email_task(name, username, email))


@celery_app.task
def celery_calculate_commission(email: str):
    _event_loop.run_until_complete(calculate_user_commission(email))
