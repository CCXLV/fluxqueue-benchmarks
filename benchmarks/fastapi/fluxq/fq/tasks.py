from benchmarks.fastapi.fluxq.mail.core import EmailConfig, get_email_client, send_email

from .core import fluxqueue


@fluxqueue.task()
async def send_email_task(subject: str, to_email: str, config: EmailConfig):
    async with get_email_client() as email_client:
        await send_email(
            email_client=email_client, to_email=to_email, subject=subject, config=config
        )
