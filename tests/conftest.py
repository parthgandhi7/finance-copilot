import io
from pathlib import Path
from uuid import uuid4

import fitz
import pytest

from app.models.document import DocumentMetadata


def _make_pdf_bytes(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@pytest.fixture
def sample_pdf_path(tmp_path: Path) -> Path:
    pdf = tmp_path / "test.pdf"
    pdf.write_bytes(
        _make_pdf_bytes(
            "POLICY DETAILS:\n"
            "Insurer: Test Insurance Co\n"
            "Policy Type: Health\n"
            "Sum Insured: 500000\n"
            "EXCLUSIONS:\n"
            "Pre-existing conditions\n"
        )
    )
    return pdf


@pytest.fixture
def mock_document(tmp_path: Path) -> DocumentMetadata:
    doc = DocumentMetadata.__new__(DocumentMetadata)
    doc.id = uuid4()
    doc.filename = "test.pdf"
    doc.content_type = "application/pdf"
    doc.file_size = 1024
    doc.storage_path = str(tmp_path / "test.pdf")
    return doc
