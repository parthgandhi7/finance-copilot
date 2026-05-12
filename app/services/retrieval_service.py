from __future__ import annotations

import hashlib
import math
import time
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentChunk, DocumentExtraction

EMBEDDING_DIM = 1536
SECTION_BOOST_TERMS = ("exclusions", "waiting", "coverage", "allocation")


@dataclass
class RetrievalTrace:
    retrieval_latency_ms: float
    classification_latency_ms: float
    insight_latency_ms: float
    top_scores: list[float]
    chunk_ids: list[str]


class RetrievalService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.lower().encode()).digest()
        vals = [(digest[i % len(digest)] / 255.0) * 2 - 1 for i in range(EMBEDDING_DIM)]
        norm = math.sqrt(sum(v * v for v in vals)) or 1.0
        return [v / norm for v in vals]

    def _cosine(self, a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    def classify_query(self, query: str) -> tuple[str, str]:
        q = query.lower()
        rules = {
            "waiting_periods": ["waiting", "ped", "pre-existing"],
            "exclusions": ["exclusion", "not covered"],
            "coverage": ["cover", "coverage", "sum insured"],
            "co_pay": ["co-pay", "copay"],
            "room_rent": ["room rent"],
            "allocation": ["allocation", "small cap", "sector"],
            "overlap": ["overlap", "duplicate"],
            "risk": ["risk", "volatility"],
            "summary": ["summary", "summarize"],
            "comparison": ["compare", "vs"],
        }
        for label, kws in rules.items():
            if any(k in q for k in kws):
                return label, "rule"
        return "clarification", "llm_fallback"

    async def retrieve(self, query: str, top_k: int = 5, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        start = time.perf_counter()
        class_start = time.perf_counter()
        query_class, route = self.classify_query(query)
        class_latency = (time.perf_counter() - class_start) * 1000

        stmt: Select[tuple[DocumentChunk]] = select(DocumentChunk)
        if filters:
            if document_type := filters.get("document_type"):
                stmt = stmt.join(DocumentExtraction, DocumentExtraction.id == DocumentChunk.extraction_id).where(
                    DocumentExtraction.structured_json["document_type_hints"].astext.ilike(f"%{document_type}%")
                )
            if chunk_type := filters.get("chunk_type"):
                stmt = stmt.where(DocumentChunk.chunk_type == chunk_type)
            if source_document_id := filters.get("source_document_id"):
                stmt = stmt.where(DocumentChunk.document_id == source_document_id)

        chunks = (await self.session.execute(stmt)).scalars().all()
        qv = self._embed(query)

        scored = []
        for chunk in chunks:
            ev = chunk.embedding if chunk.embedding else self._embed(chunk.chunk_text)
            score = self._cosine(qv, ev)
            section = (chunk.section_name or "").lower()
            if any(term in section for term in SECTION_BOOST_TERMS):
                score += 0.1
            scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        picked = scored[:top_k]

        insight_start = time.perf_counter()
        insights = self.generate_insights(query_class, picked)
        insight_latency = (time.perf_counter() - insight_start) * 1000

        retrieval_latency = (time.perf_counter() - start) * 1000
        top_scores = [round(s, 4) for s, _ in picked]
        chunk_ids = [str(c.id) for _, c in picked]

        return {
            "query": query,
            "classification": {"label": query_class, "route": route},
            "retrieved_chunks": [
                {
                    "chunk_id": str(c.id),
                    "text": c.chunk_text,
                    "similarity_score": round(s, 4),
                    "section_title": c.section_name,
                    "page_number": c.page_number,
                    "chunk_type": c.chunk_type,
                    "extraction_method": c.extraction_method,
                    "source_document_id": str(c.document_id),
                }
                for s, c in picked
            ],
            "prompt_context": "\n\n".join([f"[{str(c.id)}] {c.chunk_text[:300]}" for _, c in picked]),
            "ai_response": self.build_grounded_response(query_class, picked),
            "generated_insights": insights,
            "debug_trace": {
                "retrieval_latency_ms": round(retrieval_latency, 2),
                "classification_latency_ms": round(class_latency, 2),
                "insight_generation_latency_ms": round(insight_latency, 2),
                "top_k_scores": top_scores,
                "retrieved_chunk_ids": chunk_ids,
                "grounding_coverage": 1.0 if picked else 0.0,
            },
        }

    def build_grounded_response(self, query_class: str, picked: list[tuple[float, DocumentChunk]]) -> str:
        if not picked:
            return "No grounded evidence found in indexed documents."
        evidence = "; ".join([f"{(c.section_name or 'Section')} [Chunk: {c.id}]" for _, c in picked[:3]])
        return f"Query class `{query_class}` grounded in: {evidence}."

    def generate_insights(self, query_class: str, picked: list[tuple[float, DocumentChunk]]) -> list[dict[str, Any]]:
        insights: list[dict[str, Any]] = []
        for _, chunk in picked:
            text = chunk.chunk_text.lower()
            if "waiting period" in text and any(x in text for x in ["36", "48"]):
                insights.append({"insight_id": f"ins-{chunk.id}", "insight_type": "high_PED_waiting_period", "severity": "high", "title": "High PED waiting period detected", "description": "Waiting period appears above 24 months.", "evidence": [chunk.chunk_text[:180]], "source_chunks": [str(chunk.id)], "confidence": 0.9, "generated_by": "rule"})
            if "room rent" in text and "cap" in text:
                insights.append({"insight_id": f"ins-{chunk.id}", "insight_type": "room_rent_cap_detected", "severity": "medium", "title": "Room rent cap clause", "description": "Room rent cap clause appears present.", "evidence": [chunk.chunk_text[:180]], "source_chunks": [str(chunk.id)], "confidence": 0.85, "generated_by": "rule"})
            if query_class == "allocation" and "small cap" in text:
                insights.append({"insight_id": f"ins-{chunk.id}", "insight_type": "high_small_cap_allocation", "severity": "medium", "title": "Small-cap concentration", "description": "Small-cap allocation language detected.", "evidence": [chunk.chunk_text[:180]], "source_chunks": [str(chunk.id)], "confidence": 0.8, "generated_by": "rule"})
        return insights[:5]
