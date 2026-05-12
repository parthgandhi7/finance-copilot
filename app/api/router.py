from fastapi import APIRouter

from app.api.routes import health, retrieval, uploads

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(uploads.router, tags=["uploads"])
api_router.include_router(retrieval.router, tags=["retrieval"])
