from .configs import create_welcome_email
from .core import (
    get_email_client,
    send_email,
)


async def send_email_task(name: str, username: str, email: str):
    email_config = create_welcome_email(name, username, email)

    async with get_email_client() as client:
        await send_email(
            email_client=client,
            to_email=email,
            subject="Welcome to FluxQueue",
            config=email_config,
        )
