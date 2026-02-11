from benchmarks.tasks import calculate_user_commission, send_email_task

from .core import fluxqueue


@fluxqueue.task(name="send-email")
async def fq_send_email_task(name: str, username: str, email: str):
    await send_email_task(name, username, email)


@fluxqueue.task(name="calculate-commission")
async def fq_calculate_commission_task(email: str):
    await calculate_user_commission(email)
