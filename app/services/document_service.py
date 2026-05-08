from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.models.document import DocumentMetadata


class DocumentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_upload(self, file: UploadFile) -> DocumentMetadata:
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        extension = Path(file.filename or "").suffix
        target_name = f"{uuid4()}{extension}"
        target_path = upload_dir / target_name

        file_bytes = await file.read()
        target_path.write_bytes(file_bytes)

        document = DocumentMetadata(
            filename=file.filename or target_name,
            content_type=file.content_type or "application/octet-stream",
            file_size=len(file_bytes),
            storage_path=str(target_path),
        )
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document
