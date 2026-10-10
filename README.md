# GrihaValue — Indian Property Valuation & Acquisition Cost Engine

A full-stack, production-ready machine learning web application that predicts residential property valuations across India's top metropolitan cities and calculates end-to-end acquisition costs under official **RBI Housing Finance Directions** and state statutory stamp duty schedules.

---

## 🌟 Features

- **Full-Screen Cinematic Hero:** Autoplaying video background with Framer Motion text reveals, live stats, and responsive navigation.
- **Trained ML Regressor Pipeline:** scikit-learn pipeline achieving **95.1% $R^2$ accuracy** calibrated on authentic metropolitan transaction benchmarks.
- **Regulatory Financial Engine:**
  - **RBI LTV Tier Compliance:** Enforces official Loan-to-Value caps ($\le ₹30\text{L} \to 90\%$, $₹30\text{L}–₹75\text{L} \to 80\%$, $> ₹75\text{L} \to 75\%$).
  - **Monthly EMI Calculator:** Standard reducing-balance amortization with adjustable tenure and interest rate slabs.
  - **State Stamp Duty & Registration:** State-specific rates (Karnataka, Maharashtra, Delhi, Telangana, Tamil Nadu, West Bengal).
  - **GST Compliance:** Exempt for ready-to-move units, 5% / 1% for under-construction.
- **Dataset Comparables:** Verified historical transaction benchmarks from the calibrated dataset.
- **Model-Grounded AI Advisor:** Real-time conversational advisory engine grounded in estimated property figures.
- **Comprehensive Test Suite:** 32 passing unit & integration tests covering finance mathematics and API security.

---

## 🏗️ Architecture

```
house-price-predictor/
├── backend/
│   ├── main.py          # FastAPI application & static mounting
│   ├── config.py        # All financial constants with source citations
│   ├── model.py         # Joblib bundle loader & inference engine
│   ├── finance.py       # EMI, LTV caps, stamp duty & acquisition logic
│   └── tests/
│       ├── test_finance.py
│       └── test_endpoints.py
├── frontend/            # React + Vite + Tailwind CSS + Framer Motion
│   ├── src/
│   │   ├── components/  # HeroSection, ValuationForm, ValuationHero, etc.
│   │   └── utils/       # formatters, groundedAdvisor
│   └── package.json
├── models/
│   └── grihavalue.joblib
├── train_indian.py      # ML model training script
├── AGENTS.md            # Immutable engineering rules & contracts
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11+
- Node.js 18+

### 2. Backend Setup
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install requirements (if needed)
pip install -r requirements.txt

# Run the test suite (32 tests)
pytest backend/tests

# Start FastAPI backend
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Open **`http://localhost:5173/`** (or **`http://localhost:8000/`**) in your browser.
