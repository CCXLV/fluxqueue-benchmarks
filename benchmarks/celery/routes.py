from fastapi import APIRouter

from benchmarks.requests import BasicDataRequest

from .core import celery_calculate_commission, celery_send_email_task

celery_router = APIRouter()


@celery_router.get("/email")
def email_async(request_body: BasicDataRequest):
    celery_send_email_task.delay(  # type: ignore
        request_body.name, request_body.username, request_body.email
    )

    return {"message": "Thanks for using FluxQueue!"}


@celery_router.get("/db/{email}")
def calculate_commission(email: str):
    celery_calculate_commission.delay(email)  # type: ignore

    return {"message": "Calculations has started"}
