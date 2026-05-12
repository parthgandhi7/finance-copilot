from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.services.retrieval_service import RetrievalService

router = APIRouter()


class RetrievalRequest(BaseModel):
    query: str
    top_k: int = 5
    filters: dict[str, Any] = Field(default_factory=dict)


@router.post("/retrieval/query")
async def retrieval_query(payload: RetrievalRequest, session: AsyncSession = Depends(get_db_session)) -> dict[str, Any]:
    return await RetrievalService(session).retrieve(payload.query, payload.top_k, payload.filters)


@router.post("/retrieval/debug")
async def retrieval_debug(payload: RetrievalRequest, session: AsyncSession = Depends(get_db_session)) -> dict[str, Any]:
    return await RetrievalService(session).retrieve(payload.query, payload.top_k, payload.filters)
