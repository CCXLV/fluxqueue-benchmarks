from fastapi import APIRouter

from benchmarks.requests import WelcomeEmailBody

from .core import celery_send_email_task

celery_router = APIRouter()


@celery_router.get("/email")
def email_async(request_body: WelcomeEmailBody):
    celery_send_email_task.delay(  # type: ignore
        request_body.name, request_body.username, request_body.email
    )

    return {"message": "Thanks for using FluxQueue!"}
