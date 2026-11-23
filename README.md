# RFM CRM Automation

Portfolio showcase of a production-style pipeline: **CRM contacts + orders → RFM scoring → Google Sheets dashboard**.

Built from real auto-service operations work (amoCRM + Motowarsztat-style job data + Sheets). This public repo is a **sanitized demo** with mock data — no client PII, no API tokens.

**Stack:** Python 3.12 · RFM segmentation · CSV/JSON I/O · (optional) Google Sheets / CRM API via env

## Why it matters

Employers care about systems that:

1. Pull operational data from CRMs
2. Score customers (Recency / Frequency / Monetary)
3. Push segment totals into a living dashboard

That is exactly this pipeline.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Mock / CRM  │ --> │ RFM engine   │ --> │ Sheet / report  │
│ orders JSON │     │ rfm_scoring  │     │ CSV + segments  │
└─────────────┘     └──────────────┘     └─────────────────┘
```

### Scoring (demo defaults)

| Dimension | 1 (best) | 2 | 3 (weak) |
| --- | --- | --- | --- |
| **R** Recency | &lt;7 months | 7–12 months | 13+ months |
| **F** Frequency | 6+ jobs | 2–5 jobs | 1 job |
| **M** Monetary | ≥3000 | 500–3000 | ≤500 |

Codes are `R*100 + F*10 + M` (e.g. `111` = VIP-style). Segments: VIP, Potential VIP, Loyal, Sleeping, At risk.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt

python -m src.demo_pipeline
```

Outputs:

- `examples/out/customers_scored.csv` — per-customer RFM
- `examples/out/segment_summary.csv` — segment headcount + revenue

## Project layout

```
src/rfm_scoring.py   # pure scoring + segment map (no I/O secrets)
src/demo_pipeline.py # mock orders → score → CSV
examples/mock_orders.json
tests/test_rfm_scoring.py
.env.example         # optional live CRM / Sheets keys (never commit .env)
```

## Optional live integrations

Copy `.env.example` → `.env` and wire your own:

- CRM base URL + token
- Google service account for Sheets

The demo runs fully offline without them.

## Author

[Semen Shevchenko](https://github.com/YANKIIIII) · Full-stack · Poznań
