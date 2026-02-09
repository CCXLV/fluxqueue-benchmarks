from fastapi import APIRouter

from benchmarks.requests import WelcomeEmailBody

from .tasks import fq_send_email_async_task, fq_send_email_sync_task

fluxq_router = APIRouter()


@fluxq_router.get("/emails/sync")
def email_sync(request_body: WelcomeEmailBody):
    fq_send_email_sync_task(
        request_body.name, request_body.username, request_body.email
    )

    return {"message": "Thanks for using FluxQueue!"}


@fluxq_router.get("/emails/async")
async def email_async(request_body: WelcomeEmailBody):
    await fq_send_email_async_task(
        request_body.name, request_body.username, request_body.email
    )

    return {"message": "Thanks for using FluxQueue!"}
