"""GrihaValue FastAPI backend.

Build one endpoint at a time. See AGENTS.md for rules.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

import pandas as pd

from backend.config import (
    INTEREST_RATE_DEFAULT_PCT,
    INTEREST_RATE_MIN_PCT,
    INTEREST_RATE_MAX_PCT,
    TENURE_DEFAULT_YRS,
    TENURE_MIN_YRS,
    TENURE_MAX_YRS,
)
from backend.finance import cost_breakdown
from backend.model import get_meta, predict, get_bundle, get_showcase

app = FastAPI(
    title="GrihaValue API",
    description="Indian House Price Predictor — backed by a trained ML pipeline.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# GET /api/meta
# ---------------------------------------------------------------------------

@app.get("/api/meta")
def meta() -> dict:
    """Return all dropdown options from the trained model bundle."""
    try:
        return get_meta()
    except (FileNotFoundError, KeyError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# POST /api/estimate
# ---------------------------------------------------------------------------

class EstimateRequest(BaseModel):
    city: str
    locality: str
    bhk: int = Field(..., ge=1, le=5)
    area_sqft: float = Field(..., gt=0, le=10_000)
    bathrooms: int = Field(..., ge=1, le=10)
    property_type: str
    furnishing: str
    construction_status: str
    age_years: int = Field(..., ge=0, le=50)
    parking: int = Field(..., ge=0, le=5)
    down_payment_pct: float = Field(
        default=20.0, ge=0.0, le=100.0,
        description="Buyer's down payment as a % of property value"
    )
    annual_rate_pct: float = Field(
        default=INTEREST_RATE_DEFAULT_PCT,
        ge=INTEREST_RATE_MIN_PCT,
        le=INTEREST_RATE_MAX_PCT,
    )
    tenure_years: int = Field(
        default=TENURE_DEFAULT_YRS,
        ge=TENURE_MIN_YRS,
        le=TENURE_MAX_YRS,
    )

    @field_validator("area_sqft")
    @classmethod
    def area_reasonable_for_bhk(cls, v, info):
        bhk = info.data.get("bhk")
        if bhk and v < bhk * 200:
            raise ValueError(
                f"area_sqft={v} is implausibly small for {bhk} BHK "
                f"(minimum expected: {bhk * 200} sq.ft.)"
            )
        return v

    @field_validator("bathrooms")
    @classmethod
    def bathrooms_reasonable(cls, v, info):
        bhk = info.data.get("bhk")
        if bhk and v > bhk + 2:
            raise ValueError(
                f"bathrooms={v} is implausibly high for {bhk} BHK"
            )
        return v


class EstimateResponse(BaseModel):
    predicted_price: float
    rate_per_sqft: float
    finance: dict
    comparables: list[dict]


@app.post("/api/estimate", response_model=EstimateResponse)
def estimate(req: EstimateRequest) -> EstimateResponse:
    """Run the trained pipeline and return price + full cost breakdown."""
    try:
        bundle = get_bundle()
    except (FileNotFoundError, KeyError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Resolve locality coordinates from the bundle
    coords = bundle["locality_coords"].get(req.locality)
    if coords is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown locality '{req.locality}'. Check /api/meta for valid options."
        )

    input_df = pd.DataFrame([{
        "City": req.city,
        "Locality": req.locality,
        "BHK": req.bhk,
        "Area_SqFt": req.area_sqft,
        "Bathrooms": req.bathrooms,
        "Property_Type": req.property_type,
        "Furnishing": req.furnishing,
        "Construction_Status": req.construction_status,
        "Age_Years": req.age_years,
        "Parking": req.parking,
        "Latitude": coords["lat"],
        "Longitude": coords["lon"],
    }])

    try:
        predicted_price = predict(input_df)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {exc}") from exc

    is_uc = req.construction_status.lower() == "under construction"
    finance = cost_breakdown(
        city=req.city,
        property_value=predicted_price,
        down_payment_pct=req.down_payment_pct,
        annual_rate_pct=req.annual_rate_pct,
        tenure_years=req.tenure_years,
        is_under_construction=is_uc,
    )

    # Real comparables from the bundle — no mock data
    showcase = get_showcase(req.city)
    comps = [
        s for s in showcase
        if s.get("Locality") == req.locality and s.get("BHK") == req.bhk
    ]
    if len(comps) < 2:  # fallback: same city, BHK ±1
        comps = [
            s for s in showcase
            if abs(s.get("BHK", 0) - req.bhk) <= 1
        ]
    comps = comps[:3]

    return EstimateResponse(
        predicted_price=predicted_price,
        rate_per_sqft=predicted_price / req.area_sqft,
        finance=finance,
        comparables=comps,
    )


# ---------------------------------------------------------------------------
# POST /api/chat
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1)
    # The frontend sends back the estimate context so the chatbot is grounded
    estimate_context: dict = Field(
        ...,
        description="Must contain predicted_price, rate_per_sqft, finance, city, locality, bhk"
    )


def _build_system_prompt(ctx: dict) -> str:
    """Build a system prompt grounded entirely in model output — no invented facts."""
    price = ctx.get("predicted_price", 0)
    rate = ctx.get("rate_per_sqft", 0)
    finance = ctx.get("finance", {})
    city = ctx.get("city", "Unknown")
    locality = ctx.get("locality", "Unknown")
    bhk = ctx.get("bhk", "?")

    def inr(v: float) -> str:
        if v >= 10_000_000: return f"₹{v/10_000_000:.2f} Cr"
        if v >= 100_000: return f"₹{v/100_000:.2f} L"
        return f"₹{v:,.0f}"

    return f"""You are GrihaValue's valuation assistant. A user is asking about a property.

PROPERTY CONTEXT (from the trained model — use only these figures):
- Location: {bhk} BHK in {locality}, {city}
- Estimated Market Value: {inr(price)}
- Rate per sq.ft.: ₹{rate:,.0f}
- Down Payment: {inr(finance.get('down_payment', 0))}
- Loan Amount: {inr(finance.get('loan_amount', 0))}
- Monthly EMI: {inr(finance.get('monthly_emi', 0))}
- Stamp Duty: {inr(finance.get('stamp_duty', 0))}
- Total Acquisition Cost: {inr(finance.get('total_acquisition_cost', 0))}

RULES:
1. Answer ONLY using the figures above. Do not invent prices, appreciation rates, or locality facts.
2. If asked something you cannot answer from these figures, say: "I can only answer based on the current valuation. For that question, please consult a registered property consultant."
3. Be concise. Use Indian number format (Lakhs / Crores).
4. Never reveal that you are Claude or that an API key is being used."""


@app.post("/api/chat")
def chat(req: ChatRequest) -> StreamingResponse:
    """Stream a chatbot reply grounded in the model's estimate output.

    The Anthropic API key is read exclusively from the ANTHROPIC_API_KEY
    environment variable. It is never logged, returned, or sent to the client.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY is not set. Configure it as an environment variable on the server."
        )

    try:
        import anthropic
    except ImportError:
        raise HTTPException(status_code=500, detail="anthropic package not installed.")

    system_prompt = _build_system_prompt(req.estimate_context)
    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    def stream_reply():
        import anthropic as _anthropic
        try:
            anthro_client = _anthropic.Anthropic(api_key=api_key)
            with anthro_client.messages.stream(
                model="claude-haiku-4-5",
                max_tokens=512,
                system=system_prompt,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except _anthropic.AuthenticationError:
            # Key was invalid — do NOT yield the key or the error detail
            yield "[error: authentication failed]"
        except _anthropic.APIError as exc:
            yield f"[error: {exc.status_code}]"

    return StreamingResponse(stream_reply(), media_type="text/plain")


# ---------------------------------------------------------------------------
# Static Frontend Mounting (serves frontend directly from FastAPI)
# ---------------------------------------------------------------------------
DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(DIST_DIR), html=True), name="static")

