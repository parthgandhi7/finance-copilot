from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF


@dataclass(slots=True)
class ExtractionStep:
    method: str
    succeeded: bool
    details: str


class PDFExtractionService:
    """Hybrid extractor using PyMuPDF, Docling, and OCR fallback."""

    def __init__(self, ocr_language: str = "eng") -> None:
        self.ocr_language = ocr_language

    def extract(self, pdf_path: str | Path) -> dict[str, Any]:
        path = Path(pdf_path)
        raw_text, pages = self._extract_native_text(path)

        metadata_steps: list[ExtractionStep] = []
        metadata_steps.append(
            ExtractionStep(
                method="pymupdf",
                succeeded=bool(raw_text.strip()),
                details="Native text extraction from PDF pages",
            )
        )

        structured_sections, tables = self._extract_docling_structure(path)
        metadata_steps.append(
            ExtractionStep(
                method="docling",
                succeeded=bool(structured_sections or tables),
                details="Structural extraction for headings, sections, and tables",
            )
        )

        used_ocr = False
        if not raw_text.strip():
            ocr_text = self._extract_with_ocr(path)
            if ocr_text.strip():
                raw_text = ocr_text
                used_ocr = True
            metadata_steps.append(
                ExtractionStep(
                    method="tesseract_ocr",
                    succeeded=bool(ocr_text.strip()),
                    details="OCR fallback for scanned/image-only PDFs",
                )
            )

        if not structured_sections:
            structured_sections = self._heuristic_sections_from_text(raw_text)

        semantic_chunks = self._semantic_chunk_sections(structured_sections)

        return {
            "document_type_hints": self._infer_document_type(path.name, raw_text),
            "raw_text": raw_text,
            "structured_sections": structured_sections,
            "tables": tables,
            "semantic_chunks": semantic_chunks,
            "extraction_metadata": {
                "source_file": str(path),
                "page_count": pages,
                "used_ocr_fallback": used_ocr,
                "steps": [step.__dict__ for step in metadata_steps],
            },
        }

    def _extract_native_text(self, pdf_path: Path) -> tuple[str, int]:
        with fitz.open(pdf_path) as document:
            page_text = [page.get_text("text") for page in document]
            return "\n".join(page_text), len(document)

    def _extract_docling_structure(self, pdf_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        try:
            from docling.document_converter import DocumentConverter
        except ImportError:
            return [], []

        converter = DocumentConverter()
        result = converter.convert(str(pdf_path))

        sections: list[dict[str, Any]] = []
        tables: list[dict[str, Any]] = []

        doc = result.document
        for node in getattr(doc, "iterate_items", lambda: [])():
            label = str(getattr(node, "label", "")).lower()
            text = (getattr(node, "text", "") or "").strip()
            if not text:
                continue

            if "heading" in label or label in {"title", "section_header"}:
                sections.append({"heading": text, "content": "", "source": "docling"})
                continue

            if "table" in label:
                table_rows = getattr(node, "data", None) or []
                tables.append(
                    {
                        "title": getattr(node, "caption", None),
                        "rows": table_rows,
                        "source": "docling",
                    }
                )
                continue

            if sections:
                sections[-1]["content"] = (sections[-1]["content"] + "\n" + text).strip()
            else:
                sections.append({"heading": "Document", "content": text, "source": "docling"})

        return sections, tables

    def _extract_with_ocr(self, pdf_path: Path) -> str:
        try:
            import pytesseract
        except ImportError:
            return ""

        with fitz.open(pdf_path) as document:
            ocr_pages: list[str] = []
            for page in document:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                image_bytes = pix.tobytes("png")

                from PIL import Image
                from io import BytesIO

                image = Image.open(BytesIO(image_bytes))
                ocr_pages.append(pytesseract.image_to_string(image, lang=self.ocr_language).strip())

        return "\n".join(text for text in ocr_pages if text)

    def _heuristic_sections_from_text(self, raw_text: str) -> list[dict[str, Any]]:
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        sections: list[dict[str, Any]] = []
        current_heading = "Document"
        current_content: list[str] = []

        for line in lines:
            is_heading = line.isupper() or (len(line) < 80 and line.endswith(":"))
            if is_heading and current_content:
                sections.append({"heading": current_heading, "content": "\n".join(current_content)})
                current_heading = line.rstrip(":")
                current_content = []
            elif is_heading and not current_content:
                current_heading = line.rstrip(":")
            else:
                current_content.append(line)

        if current_content:
            sections.append({"heading": current_heading, "content": "\n".join(current_content)})

        return sections or [{"heading": "Document", "content": raw_text.strip()}]

    def _semantic_chunk_sections(self, sections: list[dict[str, Any]], chunk_size: int = 1000) -> list[dict[str, Any]]:
        chunks: list[dict[str, Any]] = []
        for section in sections:
            heading = section.get("heading", "Document")
            content = section.get("content", "")
            if not content:
                continue
            start = 0
            while start < len(content):
                end = start + chunk_size
                chunks.append(
                    {
                        "heading": heading,
                        "text": content[start:end],
                        "start_offset": start,
                        "end_offset": min(end, len(content)),
                    }
                )
                start = end
        return chunks

    def _infer_document_type(self, filename: str, raw_text: str) -> list[str]:
        text = f"{filename}\n{raw_text[:5000]}".lower()
        hints: list[str] = []
        if "insurance" in text or "policy" in text:
            hints.append("insurance_policy")
        if "consolidated account statement" in text or "cas" in text:
            hints.append("cas_statement")
        return hints or ["generic_financial_document"]
