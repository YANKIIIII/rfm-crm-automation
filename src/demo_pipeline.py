"""Offline demo: mock orders → RFM scores → CSV reports."""

from __future__ import annotations

import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path

from src.rfm_scoring import Order, score_customers, segment_summary

ROOT = Path(__file__).resolve().parents[1]
MOCK = ROOT / "examples" / "mock_orders.json"
OUT_DIR = ROOT / "examples" / "out"


def load_orders(path: Path) -> list[Order]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    orders: list[Order] = []
    for row in raw:
        orders.append(
            Order(
                customer_id=str(row["customer_id"]),
                customer_name=str(row["customer_name"]),
                order_date=datetime.strptime(row["order_date"], "%Y-%m-%d").date(),
                amount=float(row["amount"]),
            )
        )
    return orders


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    as_of = date(2026, 11, 23)
    orders = load_orders(MOCK)
    scores = score_customers(orders, as_of=as_of)
    summary = segment_summary(scores)

    customer_rows = [
        {
            "customer_id": s.customer_id,
            "customer_name": s.customer_name,
            "orders": s.orders,
            "monetary": s.monetary,
            "last_order": s.last_order.isoformat(),
            "months_since": s.months_since,
            "rfm": s.code,
            "segment": s.segment,
            "attention": s.attention,
        }
        for s in scores
    ]
    write_csv(
        OUT_DIR / "customers_scored.csv",
        customer_rows,
        [
            "customer_id",
            "customer_name",
            "orders",
            "monetary",
            "last_order",
            "months_since",
            "rfm",
            "segment",
            "attention",
        ],
    )
    write_csv(
        OUT_DIR / "segment_summary.csv",
        [dict(r) for r in summary],
        ["segment", "customers", "orders", "revenue"],
    )

    print(f"Scored {len(scores)} customers from {len(orders)} orders (as of {as_of}).")
    for row in summary:
        print(
            f"  {row['segment']}: {row['customers']} customers, "
            f"{row['orders']} orders, {row['revenue']} revenue"
        )
    print(f"Wrote {OUT_DIR / 'customers_scored.csv'}")
    print(f"Wrote {OUT_DIR / 'segment_summary.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
