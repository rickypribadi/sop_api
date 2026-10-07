from fastapi import APIRouter, Depends

from routes.endpoints import (
    worker
)

# SUBSCRIBE
api_router = APIRouter()
api_router.include_router(worker.router, prefix="/worker", tags=['worker'])