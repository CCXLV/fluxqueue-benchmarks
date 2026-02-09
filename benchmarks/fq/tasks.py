from benchmarks.mail.tasks import send_email_task

from .core import fluxqueue


@fluxqueue.task(name="send-email")
async def fq_send_email_task(name: str, username: str, email: str):
    await send_email_task(name, username, email)
