from app.services.retrieval_service import RetrievalService


class DummySession:
    pass


def test_query_classification_rule() -> None:
    label, route = RetrievalService(DummySession()).classify_query("What is the waiting period?")
    assert label == "waiting_periods"
    assert route == "rule"


def test_insight_generation_waiting_period() -> None:
    svc = RetrievalService(DummySession())

    class C:
        id = "chunk-1"
        chunk_text = "Pre-existing disease waiting period is 36 months"

    insights = svc.generate_insights("waiting_periods", [(0.9, C())])
    assert insights
    assert insights[0]["insight_type"] == "high_PED_waiting_period"
