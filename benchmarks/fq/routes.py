from fastapi import APIRouter

from benchmarks.database.core import DbSession
from benchmarks.database.models import User
from benchmarks.requests import BasicDataRequest

from .tasks import fq_send_email_task

fluxq_router = APIRouter()


@fluxq_router.get("/email")
async def email_async(request_body: BasicDataRequest):
    await fq_send_email_task(
        request_body.name, request_body.username, request_body.email
    )

    return {"message": "Thanks for using FluxQueue!"}


@fluxq_router.post("/db/register")
async def db_register(db_session: DbSession, request_body: BasicDataRequest):
    user = User(
        username=request_body.username,
        name=request_body.name,
        email=request_body.email,
    )

    db_session.add(user)
    await db_session.commit()

    return {"message": "User was registered"}
