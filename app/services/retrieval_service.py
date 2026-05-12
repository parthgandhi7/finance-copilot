from __future__ import annotations

import time
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentChunk
from app.services.embedding_service import EmbeddingService


class RetrievalService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.embedding_service = EmbeddingService()

    def classify_query(self, query: str) -> tuple[str, float, str]:
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
                return label, 0.9, "rule"
        return "clarification", 0.5, "model"

    async def retrieve(self, query: str, top_k: int = 5, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        start = time.perf_counter()
        label, conf, method = self.classify_query(query)
        query_embedding = await self.embedding_service.embed_text(query)

        stmt: Select = select(DocumentChunk, DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"))
        stmt = stmt.where(DocumentChunk.embedding.is_not(None))

        if filters and (source_document_id := filters.get("source_document_id")):
            stmt = stmt.where(DocumentChunk.document_id == source_document_id)
        if filters and (chunk_type := filters.get("chunk_type")):
            stmt = stmt.where(DocumentChunk.chunk_type == chunk_type)

        stmt = stmt.order_by("distance").limit(top_k)
        rows = (await self.session.execute(stmt)).all()

        retrieved = []
        context_parts = []
        for chunk, distance in rows:
            similarity = max(0.0, 1 - float(distance))
            retrieved.append(
                {
                    "chunk_id": str(chunk.id),
                    "document_id": str(chunk.document_id),
                    "section_title": chunk.section_name,
                    "page_number": chunk.page_number,
                    "similarity_score": round(similarity, 4),
                    "chunk_type": chunk.chunk_type,
                    "content": chunk.chunk_text,
                    "retrieval_reason": "Top cosine similarity match in pgvector index",
                }
            )
            context_parts.append(f"[{chunk.id}] {chunk.chunk_text}")

        assembled_context = "\n\n".join(context_parts)
        answer = self.build_grounded_response(label, retrieved)

        return {
            "query": query,
            "classification": {"label": label, "confidence": conf, "method": method},
            "retrieval": {
                "latency_ms": round((time.perf_counter() - start) * 1000, 2),
                "filters": filters or [],
                "chunks": retrieved,
            },
            "prompt_context": {
                "assembled_context": assembled_context,
                "estimated_tokens": max(1, len(assembled_context) // 4),
            },
            "response": {
                "answer": answer,
                "grounded": bool(retrieved),
                "citations": [
                    {"chunk_id": c["chunk_id"], "section_title": c.get("section_title"), "page_number": c.get("page_number")}
                    for c in retrieved[:5]
                ],
            },
            "insights": self.generate_insights(retrieved),
        }

    def build_grounded_response(self, query_class: str, chunks: list[dict[str, Any]]) -> str:
        if not chunks:
            return "No grounded evidence found in indexed documents."
        top = chunks[0]
        return (
            f"Based on retrieved evidence for '{query_class}', the strongest relevant section is "
            f"{top.get('section_title') or 'Untitled'} (page {top.get('page_number') or 'n/a'})."
        )

    def generate_insights(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not chunks:
            return []
        return [
            {
                "insight_id": f"coverage-{chunks[0]['chunk_id']}",
                "insight_type": "retrieval_coverage",
                "severity": "low",
                "title": "Retrieved grounded evidence",
                "description": f"Top-{len(chunks)} chunks pulled from pgvector index.",
                "source_chunks": [c["chunk_id"] for c in chunks],
                "generated_by": "rule",
            }
        ]
