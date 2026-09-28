"""Streamlit web app for the house price predictor."""

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


PROJECT_DIR = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_DIR / "house_price_model.joblib"
STYLE_PATH = PROJECT_DIR / "style.css"
ACCENT_COLOR = "#2D6A8E"


def income_band(median_income: float) -> str:
    if median_income <= 3:
        return "Low"
    if median_income <= 5:
        return "Medium"
    if median_income <= 8:
        return "High"
    return "Very high"


def load_style() -> None:
    if STYLE_PATH.exists():
        st.markdown(f"<style>{STYLE_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def field_bounds(bundle: dict, feature_name: str, fallback_min: float, fallback_max: float) -> tuple[float, float]:
    ranges = bundle.get("feature_ranges", {})
    if feature_name in ranges:
        return float(ranges[feature_name]["min"]), float(ranges[feature_name]["max"])
    return fallback_min, fallback_max


def compute_row(inputs: dict[str, float]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "MedInc": inputs["MedInc"],
                "HouseAge": inputs["HouseAge"],
                "AveRooms": inputs["AveRooms"],
                "AveBedrms": inputs["AveBedrms"],
                "Population": inputs["Population"],
                "AveOccup": inputs["AveOccup"],
                "Latitude": inputs["Latitude"],
                "Longitude": inputs["Longitude"],
                "income_band": income_band(inputs["MedInc"]),
            }
        ]
    )


def section_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="section-wrap">
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="House Price Studio", page_icon="house", layout="wide")
    load_style()

    if not MODEL_PATH.exists():
        st.error("No trained model found. Run `python train.py` first.")
        st.stop()

    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]
    defaults = bundle["feature_defaults"]

    st.markdown(
        """
        <header class="hero-shell">
          <div class="hero-left">
            <span class="hero-chip">California Housing Model</span>
            <h1>Estimate local home value with an interactive ML studio</h1>
            <p>Adjust neighborhood and property inputs, then compare scenarios in one clean workspace.</p>
          </div>
          <div class="hero-right">
            <div class="hero-stat">
              <span>Prediction engine</span>
              <strong>Random Forest + Ridge benchmark</strong>
            </div>
            <div class="hero-stat">
              <span>Target</span>
              <strong>Median house value in US dollars</strong>
            </div>
          </div>
        </header>
        """,
        unsafe_allow_html=True,
    )

    section_header(
        "Property Inputs",
        "Tune each variable and generate a fresh estimate.",
    )

    with st.form("house_features", border=False):
        col1, col2 = st.columns(2)

        medinc_min, medinc_max = field_bounds(bundle, "MedInc", 0.0, 20.0)
        age_min, age_max = field_bounds(bundle, "HouseAge", 1.0, 60.0)
        rooms_min, rooms_max = field_bounds(bundle, "AveRooms", 1.0, 20.0)
        bedrooms_min, bedrooms_max = field_bounds(bundle, "AveBedrms", 0.0, 10.0)
        pop_min, pop_max = field_bounds(bundle, "Population", 1.0, 20000.0)
        occup_min, occup_max = field_bounds(bundle, "AveOccup", 1.0, 20.0)
        lat_min, lat_max = field_bounds(bundle, "Latitude", 32.0, 42.0)
        lon_min, lon_max = field_bounds(bundle, "Longitude", -125.0, -114.0)

        with col1:
            median_income = st.slider(
                "Median income (x$10,000)",
                min_value=float(round(medinc_min, 1)),
                max_value=float(round(medinc_max, 1)),
                value=float(round(defaults["MedInc"], 1)),
                step=0.1,
            )
            house_age = st.slider(
                "Median house age (years)",
                min_value=float(round(age_min, 0)),
                max_value=float(round(age_max, 0)),
                value=float(round(defaults["HouseAge"], 0)),
                step=1.0,
            )
            average_rooms = st.slider(
                "Average rooms",
                min_value=float(round(rooms_min, 1)),
                max_value=float(round(rooms_max, 1)),
                value=float(round(defaults["AveRooms"], 1)),
                step=0.1,
            )
            average_bedrooms = st.slider(
                "Average bedrooms",
                min_value=float(round(bedrooms_min, 1)),
                max_value=float(round(bedrooms_max, 1)),
                value=float(round(defaults["AveBedrms"], 1)),
                step=0.1,
            )
        with col2:
            population = st.slider(
                "Block population",
                min_value=float(round(pop_min, 0)),
                max_value=float(round(pop_max, 0)),
                value=float(round(defaults["Population"], 0)),
                step=50.0,
            )
            average_occupancy = st.slider(
                "Average occupancy",
                min_value=float(round(occup_min, 1)),
                max_value=float(round(occup_max, 1)),
                value=float(round(defaults["AveOccup"], 1)),
                step=0.1,
            )
            latitude = st.slider(
                "Latitude",
                min_value=float(round(lat_min, 2)),
                max_value=float(round(lat_max, 2)),
                value=float(round(defaults["Latitude"], 2)),
                step=0.01,
            )
            longitude = st.slider(
                "Longitude",
                min_value=float(round(lon_min, 2)),
                max_value=float(round(lon_max, 2)),
                value=float(round(defaults["Longitude"], 2)),
                step=0.01,
            )

        submitted = st.form_submit_button("Generate estimate", use_container_width=True)

    if not submitted and "latest_estimate" in st.session_state:
        submitted = True

    if submitted:
        inputs = {
            "MedInc": median_income,
            "HouseAge": house_age,
            "AveRooms": average_rooms,
            "AveBedrms": average_bedrooms,
            "Population": population,
            "AveOccup": average_occupancy,
            "Latitude": latitude,
            "Longitude": longitude,
        }
        row = compute_row(inputs)
        estimate = float(model.predict(row)[0])

        baseline_inputs = {
            "MedInc": float(defaults["MedInc"]),
            "HouseAge": float(defaults["HouseAge"]),
            "AveRooms": float(defaults["AveRooms"]),
            "AveBedrms": float(defaults["AveBedrms"]),
            "Population": float(defaults["Population"]),
            "AveOccup": float(defaults["AveOccup"]),
            "Latitude": float(defaults["Latitude"]),
            "Longitude": float(defaults["Longitude"]),
        }
        baseline_row = compute_row(baseline_inputs)
        baseline_estimate = float(model.predict(baseline_row)[0])

        st.session_state["latest_estimate"] = estimate
        st.session_state["latest_delta"] = estimate - baseline_estimate
        st.session_state["latest_income_band"] = income_band(median_income)

        metric1, metric2, metric3 = st.columns(3)
        metric1.metric("Estimated median value", f"${estimate:,.0f}")
        metric2.metric("Vs median baseline", f"${estimate - baseline_estimate:,.0f}")
        metric3.metric("Income segment", st.session_state["latest_income_band"])

        section_header(
            "Location Preview",
            "Your selected location plotted against sampled neighborhoods.",
        )

        sample_points = pd.DataFrame(
            bundle.get(
                "showcase_samples",
                [{"Latitude": 36.8, "Longitude": -119.4, "MedInc": 3.5, "HouseAge": 20.0}],
            )
        )
        sample_points = sample_points.rename(
            columns={"Latitude": "lat", "Longitude": "lon"}
        )
        sample_points["size"] = ((sample_points["MedInc"] * 2) + 2).clip(2, 14)
        sample_points["group"] = "Sampled neighborhoods"

        selected_point = pd.DataFrame(
            [{"lat": latitude, "lon": longitude, "size": 16, "group": "Selected point"}]
        )
        map_points = pd.concat([sample_points[["lat", "lon", "size", "group"]], selected_point], ignore_index=True)
        st.map(map_points, size="size", color="#2D6A8E")

        section_header(
            "Scenario Impact",
            "Understand how one feature shift can move the estimate.",
        )
        scenario_values = [max(medinc_min, median_income - 1.5), median_income, min(medinc_max, median_income + 1.5)]
        scenario_rows = []
        labels = ["Lower income band", "Current selection", "Higher income band"]
        for label, medinc_value in zip(labels, scenario_values):
            scenario_input = inputs.copy()
            scenario_input["MedInc"] = medinc_value
            scenario_estimate = float(model.predict(compute_row(scenario_input))[0])
            scenario_rows.append(
                {
                    "Scenario": label,
                    "Median income": medinc_value,
                    "Estimated price": scenario_estimate,
                }
            )

        scenario_df = pd.DataFrame(scenario_rows).set_index("Scenario")
        st.bar_chart(scenario_df["Estimated price"], color=ACCENT_COLOR)
        st.dataframe(
            scenario_df.style.format(
                {"Median income": "{:.2f}", "Estimated price": "${:,.0f}"}
            ),
            use_container_width=True,
        )
        st.caption(f"Training winner: {bundle['model_name']}")


if __name__ == "__main__":
    main()
