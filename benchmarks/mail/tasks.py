from .configs import create_welcome_email
from .core import (
    get_email_client_async,
    get_email_client_sync,
    send_email_async,
    send_email_sync,
)


def send_email_sync_task(name: str, username: str, email: str):
    email_config = create_welcome_email(name, username, email)

    with get_email_client_sync() as client:
        send_email_sync(
            email_client=client,
            to_email=email,
            subject="Welcome to FluxQueue",
            config=email_config,
        )


async def send_email_async_task(name: str, username: str, email: str):
    email_config = create_welcome_email(name, username, email)

    async with get_email_client_async() as client:
        await send_email_async(
            email_client=client,
            to_email=email,
            subject="Welcome to FluxQueue",
            config=email_config,
        )
