import io
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import fitz
import pytest
from httpx import ASGITransport, AsyncClient

from app.db.session import get_db_session
from app.main import app


def _make_pdf_bytes() -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Test document")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _make_mock_document(storage_path: str = "/tmp/test.pdf") -> MagicMock:
    doc = MagicMock()
    doc.id = uuid4()
    doc.filename = "test.pdf"
    doc.content_type = "application/pdf"
    doc.file_size = 1024
    doc.storage_path = storage_path
    return doc


FAKE_EXTRACTION = {
    "document_type_hints": ["generic_financial_document"],
    "raw_text": "Test document",
    "structured_sections": [{"heading": "Document", "content": "Test document", "source": "heuristic"}],
    "tables": [],
    "semantic_chunks": [],
    "structured_financial_extraction": {
        "attempts": 1,
        "validated": True,
        "data": {"insurance": {}, "mutual_funds": {}},
        "schema": "FinancialDocumentExtraction",
    },
    "extraction_metadata": {
        "source_file": "/tmp/test.pdf",
        "page_count": 1,
        "used_ocr_fallback": False,
        "steps": [{"method": "pymupdf", "succeeded": True, "details": "Native text extraction from PDF pages"}],
    },
}


@pytest.fixture
def mock_db() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def pdf_file() -> bytes:
    return _make_pdf_bytes()


async def test_upload_and_extract_returns_200(mock_db: AsyncMock, pdf_file: bytes, tmp_path: Path) -> None:
    stored_pdf = tmp_path / "stored.pdf"
    stored_pdf.write_bytes(pdf_file)
    mock_doc = _make_mock_document(storage_path=str(stored_pdf))

    with (
        patch("app.api.routes.uploads.DocumentService") as MockDocSvc,
        patch("app.api.routes.uploads.PDFExtractionService") as MockExtSvc,
    ):
        MockDocSvc.return_value.save_upload = AsyncMock(return_value=mock_doc)
        MockExtSvc.return_value.extract = MagicMock(return_value=FAKE_EXTRACTION)
        app.dependency_overrides[get_db_session] = lambda: mock_db

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/documents/upload-and-extract",
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
            )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert "extracted" in data
    assert data["extracted"]["raw_text"] == "Test document"


async def test_upload_and_extract_response_shape(mock_db: AsyncMock, pdf_file: bytes, tmp_path: Path) -> None:
    """Regression: model_validate on ORM object raised 'extracted field required'."""
    stored_pdf = tmp_path / "stored.pdf"
    stored_pdf.write_bytes(pdf_file)
    mock_doc = _make_mock_document(storage_path=str(stored_pdf))

    with (
        patch("app.api.routes.uploads.DocumentService") as MockDocSvc,
        patch("app.api.routes.uploads.PDFExtractionService") as MockExtSvc,
    ):
        MockDocSvc.return_value.save_upload = AsyncMock(return_value=mock_doc)
        MockExtSvc.return_value.extract = MagicMock(return_value=FAKE_EXTRACTION)
        app.dependency_overrides[get_db_session] = lambda: mock_db

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/documents/upload-and-extract",
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
            )

    app.dependency_overrides.clear()

    data = response.json()
    for field in ("id", "filename", "content_type", "file_size", "storage_path", "extracted"):
        assert field in data, f"Missing field in response: {field}"


async def test_upload_only_returns_200(mock_db: AsyncMock, pdf_file: bytes) -> None:
    mock_doc = _make_mock_document()

    with patch("app.api.routes.uploads.DocumentService") as MockDocSvc:
        MockDocSvc.return_value.save_upload = AsyncMock(return_value=mock_doc)
        app.dependency_overrides[get_db_session] = lambda: mock_db

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
            )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["filename"] == "test.pdf"


async def test_upload_requires_file(mock_db: AsyncMock) -> None:
    app.dependency_overrides[get_db_session] = lambda: mock_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/documents/upload")

    app.dependency_overrides.clear()

    assert response.status_code == 422
