"""Model loading and inference utilities for GrihaValue.

The bundle is loaded exactly once at startup via the module-level singleton.
All inference goes through `predict()`.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from backend.config import MODEL_BUNDLE_PATH


@lru_cache(maxsize=1)
def get_bundle() -> dict[str, Any]:
    """Load the joblib bundle once and cache it for the lifetime of the process."""
    path = Path(MODEL_BUNDLE_PATH)
    if not path.exists():
        raise FileNotFoundError(
            f"Model bundle not found at '{path.resolve()}'. "
            "Run 'python train_indian.py' to generate it."
        )
    bundle = joblib.load(path)

    # Hard fail on missing required keys — silent fallback is forbidden (AGENTS.md)
    required = {"model", "city_locality_map", "locality_coords",
                "property_types", "furnishing_options", "status_options",
                "showcase_samples"}
    missing = required - bundle.keys()
    if missing:
        raise KeyError(
            f"Model bundle is missing required keys: {missing}. "
            "Re-run train_indian.py to regenerate."
        )
    return bundle


def get_meta() -> dict[str, Any]:
    """Return dropdown options and defaults read from the trained bundle."""
    bundle = get_bundle()
    return {
        "cities": list(bundle["city_locality_map"].keys()),
        "city_locality_map": bundle["city_locality_map"],
        "property_types": bundle["property_types"],
        "furnishing_options": bundle["furnishing_options"],
        "status_options": bundle["status_options"],
        "r2_score": bundle.get("r2_score"),
        "model_name": bundle.get("model_name"),
    }


def predict(input_df: pd.DataFrame) -> float:
    """Run the trained pipeline and return a predicted price in INR."""
    bundle = get_bundle()
    model = bundle["model"]
    return float(model.predict(input_df)[0])


def get_showcase(city: str) -> list[dict]:
    """Return showcase samples for a given city from the bundle."""
    bundle = get_bundle()
    samples = bundle.get("showcase_samples", [])
    return [s for s in samples if s.get("City") == city]
