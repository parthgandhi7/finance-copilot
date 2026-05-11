from pathlib import Path

import pytest

from app.services.pdf_extraction_service import PDFExtractionService


def test_extract_returns_all_keys(sample_pdf_path: Path) -> None:
    result = PDFExtractionService().extract(sample_pdf_path)
    for key in ("raw_text", "structured_sections", "tables", "document_type_hints", "extraction_metadata"):
        assert key in result, f"Missing key: {key}"


def test_extract_raw_text_not_empty(sample_pdf_path: Path) -> None:
    result = PDFExtractionService().extract(sample_pdf_path)
    assert result["raw_text"].strip(), "raw_text should not be empty for a text PDF"


def test_extraction_metadata_has_pymupdf_step(sample_pdf_path: Path) -> None:
    result = PDFExtractionService().extract(sample_pdf_path)
    steps = result["extraction_metadata"]["steps"]
    methods = [s["method"] for s in steps]
    assert "pymupdf" in methods


def test_extraction_metadata_steps_are_dicts(sample_pdf_path: Path) -> None:
    """Regression: ExtractionStep.slots=True broke __dict__ serialisation."""
    result = PDFExtractionService().extract(sample_pdf_path)
    for step in result["extraction_metadata"]["steps"]:
        assert isinstance(step, dict)
        assert {"method", "succeeded", "details"} == step.keys()


def test_structured_sections_are_populated(sample_pdf_path: Path) -> None:
    result = PDFExtractionService().extract(sample_pdf_path)
    sections = result["structured_sections"]
    assert isinstance(sections, list)
    assert len(sections) > 0
    for s in sections:
        assert "heading" in s
        assert "content" in s


def test_document_type_hints_insurance(sample_pdf_path: Path) -> None:
    result = PDFExtractionService().extract(sample_pdf_path)
    assert "insurance_policy" in result["document_type_hints"]


def test_infer_document_type_cas() -> None:
    svc = PDFExtractionService()
    hints = svc._infer_document_type("cas_2024.pdf", "consolidated account statement mutual fund")
    assert "cas_statement" in hints


def test_infer_document_type_generic() -> None:
    svc = PDFExtractionService()
    hints = svc._infer_document_type("random.pdf", "nothing special here")
    assert hints == ["generic_financial_document"]


def test_docling_fallback_returns_empty_on_bad_path(tmp_path: Path) -> None:
    """Regression: docling errors outside ImportError used to propagate as 500."""
    sections, tables = PDFExtractionService()._extract_docling_structure(tmp_path / "nonexistent.pdf")
    assert sections == []
    assert tables == []


def test_heuristic_sections_with_headers() -> None:
    svc = PDFExtractionService()
    text = "INTRODUCTION:\nThis is intro.\nDETAILS:\nLine one.\nLine two."
    sections = svc._heuristic_sections_from_text(text)
    assert any(s["heading"] == "INTRODUCTION" for s in sections)
    assert all("content" in s for s in sections)


def test_heuristic_sections_fallback_on_plain_text() -> None:
    svc = PDFExtractionService()
    text = "just some plain text with no headings"
    sections = svc._heuristic_sections_from_text(text)
    assert len(sections) >= 1
    assert sections[0]["content"]


def test_semantic_chunks_split_large_content() -> None:
    svc = PDFExtractionService()
    long_content = "x" * 2500
    sections = [{"heading": "Section", "content": long_content}]
    chunks = svc._semantic_chunk_sections(sections, chunk_size=1000)
    assert len(chunks) == 3
    assert all(c["heading"] == "Section" for c in chunks)


def test_ocr_fallback_graceful_on_no_tesseract(sample_pdf_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """If pytesseract is not installed, OCR returns empty string without crashing."""
    import sys
    monkeypatch.setitem(sys.modules, "pytesseract", None)  # simulate missing package
    result = PDFExtractionService()._extract_with_ocr(sample_pdf_path)
    assert isinstance(result, str)
