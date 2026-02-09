from fastapi import APIRouter

from benchmarks.celery.routes import celery_router
from benchmarks.fq.routes import fluxq_router

api_router = APIRouter()

api_router.include_router(
    fluxq_router, prefix="/fluxqueue", tags=["fluxqueue"]
)
api_router.include_router(celery_router, prefix="/celery", tags=["celery"])
