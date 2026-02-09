from benchmarks.mail.tasks import send_email_async_task, send_email_sync_task

from .core import fluxqueue


@fluxqueue.task(name="send-email-sync")
def fq_send_email_sync_task(name: str, username: str, email: str):
    send_email_sync_task(name, username, email)


@fluxqueue.task(name="send-email-async")
async def fq_send_email_async_task(name: str, username: str, email: str):
    await send_email_async_task(name, username, email)
