"""Pure RFM scoring and segment mapping (no network, no secrets)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

# R: months since last order | F: order count | M: total spend
RFM_GROUPS: Tuple[Tuple[str, str, Tuple[int, ...]], ...] = (
    ("VIP", "Keep", (111, 112, 121, 122, 211)),
    ("Potential VIP", "Watch", (113, 123, 131, 132, 212, 221)),
    ("Loyal", "Keep", (213, 222, 223, 231, 232, 233)),
    ("Sleeping", "Watch", (311, 312, 313, 321, 322, 323)),
    ("At risk", "Critical", (133, 331, 332, 333)),
)

SEGMENT_BY_RFM: Dict[int, Tuple[str, str]] = {
    code: (name, attention) for name, attention, codes in RFM_GROUPS for code in codes
}


@dataclass(frozen=True)
class Order:
    customer_id: str
    customer_name: str
    order_date: date
    amount: float


@dataclass
class CustomerScore:
    customer_id: str
    customer_name: str
    orders: int
    monetary: float
    last_order: date
    months_since: int
    r: int
    f: int
    m: int
    code: int
    segment: str
    attention: str


def score_recency(months_since: int) -> int:
    if months_since < 7:
        return 1
    if months_since <= 12:
        return 2
    return 3


def score_frequency(order_count: int) -> int:
    if order_count >= 6:
        return 1
    if order_count >= 2:
        return 2
    return 3


def score_monetary(total: float) -> int:
    if total >= 3000:
        return 1
    if total > 500:
        return 2
    return 3


def months_between(as_of: date, last: date) -> int:
    return max(0, (as_of.year - last.year) * 12 + (as_of.month - last.month))


def score_customers(
    orders: Sequence[Order],
    *,
    as_of: Optional[date] = None,
) -> List[CustomerScore]:
    """Aggregate orders per customer and assign RFM codes."""
    as_of = as_of or date.today()
    buckets: Dict[str, List[Order]] = {}
    for order in orders:
        buckets.setdefault(order.customer_id, []).append(order)

    scored: List[CustomerScore] = []
    for customer_id, rows in buckets.items():
        last = max(r.order_date for r in rows)
        monetary = sum(r.amount for r in rows)
        count = len(rows)
        months = months_between(as_of, last)
        r = score_recency(months)
        f = score_frequency(count)
        m = score_monetary(monetary)
        code = 100 * r + 10 * f + m
        segment, attention = SEGMENT_BY_RFM.get(code, ("Uncategorized", "Watch"))
        scored.append(
            CustomerScore(
                customer_id=customer_id,
                customer_name=rows[0].customer_name,
                orders=count,
                monetary=round(monetary, 2),
                last_order=last,
                months_since=months,
                r=r,
                f=f,
                m=m,
                code=code,
                segment=segment,
                attention=attention,
            )
        )
    scored.sort(key=lambda c: (c.segment, -c.monetary, c.customer_name))
    return scored


def segment_summary(scores: Iterable[CustomerScore]) -> List[Dict[str, object]]:
    totals: Dict[str, Dict[str, object]] = {}
    for row in scores:
        bucket = totals.setdefault(
            row.segment,
            {"segment": row.segment, "customers": 0, "orders": 0, "revenue": 0.0},
        )
        bucket["customers"] = int(bucket["customers"]) + 1
        bucket["orders"] = int(bucket["orders"]) + row.orders
        bucket["revenue"] = float(bucket["revenue"]) + row.monetary
    order = [name for name, _att, _codes in RFM_GROUPS] + ["Uncategorized"]
    return sorted(
        ({**v, "revenue": round(float(v["revenue"]), 2)} for v in totals.values()),
        key=lambda x: order.index(str(x["segment"])) if str(x["segment"]) in order else 99,
    )
