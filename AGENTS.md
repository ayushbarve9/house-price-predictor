# GrihaValue — Project Rules for AI Agents

## Non-Negotiable Rules

- **No hardcoded data.** Never hardcode prices, locations, model outputs, or category labels. Read them from the trained bundle (`models/grihavalue.joblib`) or the API at runtime.
- **Single source of truth for constants.** Financial constants (interest rate bounds, LTV tiers, stamp duty percentages) live only in `backend/config.py`. Every constant must have a source comment and the retrieval date.
- **No secrets in frontend code.** API keys (Anthropic, etc.) are read from environment variables on the backend only. The browser must never receive or transmit a key.
- **No mock, random, or placeholder data.** Anywhere in the codebase. Comparables come from the trained dataset. Chatbot answers come from the model's real output. If real data is unavailable, return an empty result with a clear message.
- **Every endpoint returns typed errors.** Use HTTP status codes correctly (400 for bad input, 422 for validation, 500 for server fault). The frontend must handle loading, error, and empty states explicitly.
- **Prove it before marking done.** Run the relevant tests and paste the output. Do not say "it should work."
- **Minimal diffs.** Make the smallest change that completes the task. Do not refactor unrelated files. Do not touch files not in the plan.

## Architecture

```
house-price-predictor/
├── backend/
│   ├── main.py          # FastAPI app
│   ├── config.py        # All constants with source comments
│   ├── model.py         # Model loading and inference
│   ├── finance.py       # EMI, LTV, stamp duty logic
│   └── tests/
│       ├── test_finance.py
│       ├── test_endpoints.py
│       └── test_model.py
├── frontend/
│   └── (React + Vite + Tailwind + shadcn/ui)
├── models/
│   └── grihavalue.joblib
├── train_indian.py
├── AGENTS.md            # This file
└── README.md
```

## API Contract

| Endpoint | Method | Purpose |
|---|---|---|
| `GET /api/meta` | GET | Return dropdown options from the model bundle |
| `POST /api/estimate` | POST | Run the trained pipeline and return valuation |
| `POST /api/chat` | POST | Stream a model-grounded chatbot reply |

## Finance Constants Source

- **LTV tiers:** RBI Master Direction – Housing Finance, Annex I. https://www.rbi.org.in/Scripts/BS_ViewMasCirculardetails.aspx?id=12513
- **Stamp Duty & Registration:** State government schedules (stored per-city in config.py). Rates as of October 2026.
- **Interest rate range:** SBI/HDFC published home loan rates, October 2026.

## What "Real" Means Here

| Feature | Status |
|---|---|
| Model inputs/outputs | ✅ Real — trained pipeline |
| Comparables | ✅ Real — from training dataset, with date |
| Government stamp duty | ✅ Real — documented constant in config.py |
| Geocoding | ✅ OSM Nominatim (rate-limited, cached) |
| Live listings | ❌ Not legal — not built |
| Chatbot | ✅ Anthropic API, grounded in model output only |
