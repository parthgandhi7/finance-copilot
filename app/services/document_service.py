from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.models.document import Document, DocumentStatus


class DocumentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_upload(self, file: UploadFile) -> Document:
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        extension = Path(file.filename or "").suffix
        target_name = f"{uuid4()}{extension}"
        target_path = upload_dir / target_name

        file_bytes = await file.read()
        target_path.write_bytes(file_bytes)

        document = Document(
            filename=file.filename or target_name,
            content_type=file.content_type or "application/octet-stream",
            file_size=len(file_bytes),
            storage_path=str(target_path),
            status=DocumentStatus.uploaded,
        )
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def get_document(self, document_id: UUID) -> Document:
        result = await self.session.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()
        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
