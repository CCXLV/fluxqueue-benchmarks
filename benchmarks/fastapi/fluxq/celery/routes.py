from fastapi import APIRouter

from benchmarks.fastapi.fluxq.mail.configs import create_welcome_email
from benchmarks.fastapi.fluxq.requests import WelcomeEmailBody

from .core import send_email_task

celery_router = APIRouter()


@celery_router.post("/emails/welcome")
def welcome_email(request_body: WelcomeEmailBody):
    email_config = create_welcome_email(
        request_body.name, request_body.username, request_body.email
    )

    send_email_task.delay("Welcome to FluxQueue", request_body.email, email_config)  # type: ignore

    return {"message": "Thanks for using FluxQueue!"}
