from datetime import date

from src.rfm_scoring import (
    Order,
    score_customers,
    score_frequency,
    score_monetary,
    score_recency,
    segment_summary,
)


def test_score_axes() -> None:
    assert score_recency(3) == 1
    assert score_recency(9) == 2
    assert score_recency(14) == 3
    assert score_frequency(6) == 1
    assert score_frequency(3) == 2
    assert score_frequency(1) == 3
    assert score_monetary(3000) == 1
    assert score_monetary(800) == 2
    assert score_monetary(100) == 3


def test_pipeline_segments() -> None:
    orders = [
        Order("a", "A", date(2026, 10, 1), 1000),
        Order("a", "A", date(2026, 8, 1), 1000),
        Order("a", "A", date(2026, 6, 1), 1000),
        Order("a", "A", date(2026, 4, 1), 1000),
        Order("a", "A", date(2026, 2, 1), 1000),
        Order("a", "A", date(2025, 12, 1), 1000),
        Order("b", "B", date(2024, 1, 1), 50),
    ]
    scores = score_customers(orders, as_of=date(2026, 11, 23))
    by_id = {s.customer_id: s for s in scores}
    assert by_id["a"].code == 111
    assert by_id["a"].segment == "VIP"
    assert by_id["b"].segment in {"At risk", "Sleeping", "Uncategorized"}
    summary = segment_summary(scores)
    assert sum(int(r["customers"]) for r in summary) == 2
