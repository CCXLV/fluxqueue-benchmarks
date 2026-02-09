from fastapi import APIRouter

from benchmarks.requests import WelcomeEmailBody

from .core import send_email_task_async, send_email_task_sync

celery_router = APIRouter()


@celery_router.get("/emails/sync")
def email_sync(request_body: WelcomeEmailBody):
    send_email_task_sync.delay(  # type: ignore
        request_body.name, request_body.username, request_body.email
    )

    return {"message": "Thanks for using FluxQueue!"}


@celery_router.get("/emails/async")
def email_async(request_body: WelcomeEmailBody):
    send_email_task_async.delay(  # type: ignore
        request_body.name, request_body.username, request_body.email
    )

    return {"message": "Thanks for using FluxQueue!"}
