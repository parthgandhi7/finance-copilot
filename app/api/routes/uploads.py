from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.services.document_service import DocumentService

router = APIRouter()


class UploadResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    file_size: int
    storage_path: str


@router.post("/documents/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
) -> UploadResponse:
    document = await DocumentService(session).save_upload(file)
    return UploadResponse.model_validate(document, from_attributes=True)
