from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient

from app.db.session import get_db_session
from app.main import app


async def test_retrieval_debug_shape() -> None:
    fake = {
        "query": "test",
        "retrieved_chunks": [{"chunk_id": "1", "similarity_score": 0.9}],
        "prompt_context": "ctx",
        "ai_response": "resp",
        "generated_insights": [],
        "debug_trace": {"retrieval_latency_ms": 1.2},
        "classification": {"label": "summary", "route": "rule"},
    }
    with patch("app.api.routes.retrieval.RetrievalService") as svc:
        svc.return_value.retrieve = AsyncMock(return_value=fake)
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/retrieval/debug", json={"query": "test", "top_k": 5, "filters": {}})
    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "test"
    assert "retrieved_chunks" in body
