from fastapi import APIRouter

from benchmarks.requests import BasicDataRequest

from .tasks import fq_calculate_commission_task, fq_send_email_task

fluxq_router = APIRouter()


@fluxq_router.get("/email")
async def email_async(request_body: BasicDataRequest):
    await fq_send_email_task(
        request_body.name, request_body.username, request_body.email
    )

    return {"message": "Thanks for using FluxQueue!"}


@fluxq_router.get("/db/{email}")
async def calculate_commission(email: str):
    await fq_calculate_commission_task(email)

    return {"message": "Calculations has started"}
