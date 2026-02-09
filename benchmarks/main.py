from fastapi import FastAPI

from benchmarks.api import api_router

api = FastAPI()

api.include_router(api_router)
