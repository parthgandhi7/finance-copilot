from __future__ import annotations

import hashlib
import math
from typing import Protocol

from app.core.settings import settings

EMBEDDING_DIM = 1536


class EmbeddingProvider(Protocol):
    async def embed(self, text: str) -> list[float]: ...


class DeterministicEmbeddingProvider:
    async def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.lower().encode()).digest()
        vals = [(digest[i % len(digest)] / 255.0) * 2 - 1 for i in range(EMBEDDING_DIM)]
        norm = math.sqrt(sum(v * v for v in vals)) or 1.0
        return [v / norm for v in vals]


class OpenAIEmbeddingProvider:
    def __init__(self) -> None:
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def embed(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(model=settings.embedding_model, input=text)
        return list(response.data[0].embedding)


class EmbeddingService:
    def __init__(self) -> None:
        if settings.openai_api_key:
            self.provider: EmbeddingProvider = OpenAIEmbeddingProvider()
        else:
            self.provider = DeterministicEmbeddingProvider()

    async def embed_text(self, text: str) -> list[float]:
        return await self.provider.embed(text)

    async def embed_chunks(self, chunks: list[str]) -> list[list[float]]:
        return [await self.embed_text(chunk) for chunk in chunks]
