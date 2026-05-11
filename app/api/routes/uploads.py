from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.services.document_service import DocumentService
from app.services.pdf_extraction_service import PDFExtractionService

router = APIRouter()


class UploadResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    file_size: int
    storage_path: str


class ExtractedDocumentResponse(UploadResponse):
    extracted: dict[str, Any]


@router.post("/documents/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
) -> UploadResponse:
    document = await DocumentService(session).save_upload(file)
    return UploadResponse.model_validate(document, from_attributes=True)


@router.post("/documents/upload-and-extract", response_model=ExtractedDocumentResponse)
async def upload_and_extract_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
) -> ExtractedDocumentResponse:
    document = await DocumentService(session).save_upload(file)
    extraction = PDFExtractionService().extract(document.storage_path)
    return ExtractedDocumentResponse(
        id=document.id,
        filename=document.filename,
        content_type=document.content_type,
        file_size=document.file_size,
        storage_path=document.storage_path,
        extracted=extraction,
    )
