from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal, get_db_session
from app.models.document import DocumentChunk, DocumentExtraction, DocumentStatus
from app.services.document_service import DocumentService
from app.services.pdf_extraction_service import PDFExtractionService

router = APIRouter()


class UploadResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    file_size: int
    storage_path: str
    status: DocumentStatus


class StatusResponse(BaseModel):
    id: UUID
    status: DocumentStatus


async def _run_extraction_job(document_id: UUID) -> None:
    async with AsyncSessionLocal() as session:
        service = DocumentService(session)
        document = await service.get_document(document_id)
        document.status = DocumentStatus.processing
        await session.commit()

        try:
            extraction = PDFExtractionService().extract(document.storage_path)
            version_result = await session.execute(
                select(func.coalesce(func.max(DocumentExtraction.extraction_version), 0)).where(
                    DocumentExtraction.document_id == document.id
                )
            )
            next_version = int(version_result.scalar_one()) + 1

            extraction_row = DocumentExtraction(
                document_id=document.id,
                raw_text=extraction["raw_text"],
                structured_json={
                    "document_type_hints": extraction.get("document_type_hints", []),
                    "structured_sections": extraction.get("structured_sections", []),
                    "tables": extraction.get("tables", []),
                    "structured_financial_extraction": extraction.get("structured_financial_extraction", {}),
                },
                extraction_metadata=extraction.get("extraction_metadata", {}),
                extraction_version=next_version,
            )
            session.add(extraction_row)
            await session.flush()

            for chunk in extraction.get("semantic_chunks", []):
                session.add(
                    DocumentChunk(
                        document_id=document.id,
                        extraction_id=extraction_row.id,
                        chunk_text=chunk.get("text", ""),
                        section_name=chunk.get("heading"),
                        page_number=chunk.get("page_number"),
                        chunk_type=chunk.get("chunk_type", "paragraph"),
                        extraction_method="rule_based",
                    )
                )

            document.status = DocumentStatus.extracted
            await session.commit()
        except Exception as exc:
            document.status = DocumentStatus.failed
            await session.commit()
            raise exc


@router.post("/documents/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
) -> UploadResponse:
    document = await DocumentService(session).save_upload(file)
    status = getattr(document, "status", DocumentStatus.uploaded)
    return UploadResponse(
        id=document.id,
        filename=document.filename,
        content_type=document.content_type,
        file_size=document.file_size,
        storage_path=document.storage_path,
        status=status if isinstance(status, DocumentStatus) else DocumentStatus.uploaded,
    )


@router.post("/documents/{document_id}/extract", response_model=StatusResponse)
async def extract_document(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
) -> StatusResponse:
    document = await DocumentService(session).get_document(document_id)
    if document.status == DocumentStatus.processing:
        raise HTTPException(status_code=409, detail="Extraction already in progress")

    background_tasks.add_task(_run_extraction_job, document.id)
    return StatusResponse(id=document.id, status=DocumentStatus.processing)


@router.get("/documents/{document_id}/status", response_model=StatusResponse)
async def extraction_status(document_id: UUID, session: AsyncSession = Depends(get_db_session)) -> StatusResponse:
    document = await DocumentService(session).get_document(document_id)
    return StatusResponse(id=document.id, status=document.status)


@router.get("/documents/{document_id}/structured")
async def structured_data(document_id: UUID, session: AsyncSession = Depends(get_db_session)) -> dict[str, Any]:
    await DocumentService(session).get_document(document_id)
    result = await session.execute(
        select(DocumentExtraction).where(DocumentExtraction.document_id == document_id).order_by(desc(DocumentExtraction.created_at)).limit(1)
    )
    extraction = result.scalar_one_or_none()
    if extraction is None:
        raise HTTPException(status_code=404, detail="No extraction found")
    return extraction.structured_json


@router.get("/documents/{document_id}/metadata")
async def extraction_metadata(document_id: UUID, session: AsyncSession = Depends(get_db_session)) -> dict[str, Any]:
    await DocumentService(session).get_document(document_id)
    result = await session.execute(
        select(DocumentExtraction).where(DocumentExtraction.document_id == document_id).order_by(desc(DocumentExtraction.created_at)).limit(1)
    )
    extraction = result.scalar_one_or_none()
    if extraction is None:
        raise HTTPException(status_code=404, detail="No extraction found")
    return extraction.extraction_metadata


@router.get("/documents/{document_id}/chunks")
async def extraction_chunks(document_id: UUID, session: AsyncSession = Depends(get_db_session)) -> list[dict[str, Any]]:
    extraction_result = await session.execute(
        select(DocumentExtraction).where(DocumentExtraction.document_id == document_id).order_by(desc(DocumentExtraction.created_at)).limit(1)
    )
    extraction = extraction_result.scalar_one_or_none()
    if extraction is None:
        raise HTTPException(status_code=404, detail="No extraction found")

    chunks_result = await session.execute(select(DocumentChunk).where(DocumentChunk.extraction_id == extraction.id))
    chunks = chunks_result.scalars().all()
    return [
        {
            "id": str(chunk.id),
            "chunk_text": chunk.chunk_text,
            "section_name": chunk.section_name,
            "page_number": chunk.page_number,
            "chunk_type": chunk.chunk_type,
            "extraction_method": chunk.extraction_method,
        }
        for chunk in chunks
    ]


@router.post("/documents/upload-and-extract")
async def upload_and_extract_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    document = await DocumentService(session).save_upload(file)
    extraction = PDFExtractionService().extract(document.storage_path)
    return {
        "id": str(document.id),
        "filename": document.filename,
        "content_type": document.content_type,
        "file_size": document.file_size,
        "storage_path": document.storage_path,
        "status": document.status,
        "extracted": extraction,
    }
