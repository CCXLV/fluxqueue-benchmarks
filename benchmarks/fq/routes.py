from fastapi import APIRouter

from benchmarks.requests import WelcomeEmailBody

from .tasks import fq_send_email_task

fluxq_router = APIRouter()


@fluxq_router.get("/email")
async def email_async(request_body: WelcomeEmailBody):
    await fq_send_email_task(
        request_body.name, request_body.username, request_body.email
    )

    return {"message": "Thanks for using FluxQueue!"}
