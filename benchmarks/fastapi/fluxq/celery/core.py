import asyncio

from celery import Celery

from benchmarks.fastapi.fluxq.mail.core import EmailConfig, get_email_client, send_email

celery_app = Celery(broker="redis://localhost:6379/0")


async def _send_email(subject: str, to_email: str, config: EmailConfig):
    async with get_email_client() as email_client:
        await send_email(
            email_client=email_client, to_email=to_email, subject=subject, config=config
        )


@celery_app.task
def send_email_task(subject: str, to_email: str, config: EmailConfig):
    asyncio.run(_send_email(subject, to_email, config))
