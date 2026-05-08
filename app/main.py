from fastapi import FastAPI

from app.api.router import api_router
from app.core.logging import configure_logging
from app.core.settings import settings

configure_logging()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router, prefix=settings.api_prefix)
