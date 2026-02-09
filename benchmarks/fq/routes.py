from fastapi import APIRouter

from benchmarks.mail.configs import create_welcome_email
from benchmarks.requests import WelcomeEmailBody

from .tasks import send_email_task

fluxq_router = APIRouter()


@fluxq_router.post("/emails/welcome")
async def welcome_email(request_body: WelcomeEmailBody):
    email_config = create_welcome_email(
        request_body.name, request_body.username, request_body.email
    )

    await send_email_task(
        "Welcome to FluxQueue", request_body.email, email_config
    )

    return {"message": "Thanks for using FluxQueue!"}
