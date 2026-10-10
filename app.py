"""Streamlit web app for GrihaValue — Indian House Price Predictor Studio."""

from pathlib import Path
import joblib
import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk
from config import FINANCE, DEFAULT_CITY

PROJECT_DIR = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_DIR / "indian_house_price_model.joblib"
STYLE_PATH = PROJECT_DIR / "style.css"
ACCENT_COLOR = "#0F52BA"

@st.cache_resource
def load_model_bundle():
    """Cache the model bundle loading to prevent disk I/O on every interaction."""
    if not MODEL_PATH.exists():
        st.error("Model file not found. Please run `python train_indian.py` first.")
        st.stop()
    return joblib.load(MODEL_PATH)

def format_inr(amount: float) -> str:
    if amount >= 10_000_000:
        return f"₹{amount / 10_000_000:.2f} Cr"
    elif amount >= 100_000:
        return f"₹{amount / 100_000:.2f} L"
    return f"₹{amount:,.0f}"

def calculate_ltv(property_value: float) -> float:
    for threshold, ltv in FINANCE["ltv_tiers"]:
        if property_value <= threshold:
            return ltv
    return FINANCE["ltv_tiers"][-1][1]

def estimate_emi(principal: float, annual_rate_pct: float, years: int) -> float:
    r = annual_rate_pct / 12 / 100
    n = years * 12
    if r == 0:
        return principal / n
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)

def price_tier(price: float, city_prices: pd.Series) -> str:
    if city_prices.empty:
        if price < 5_000_000: return "Affordable Housing"
        elif price < 15_000_000: return "Mid-Segment"
        elif price < 35_000_000: return "Premium / Upper Mid"
        return "Ultra Luxury"
    
    p33 = city_prices.quantile(0.33)
    p66 = city_prices.quantile(0.66)
    p90 = city_prices.quantile(0.90)
    
    if price < p33: return "Affordable Housing"
    elif price < p66: return "Mid-Segment"
    elif price < p90: return "Premium / Upper Mid"
    return "Ultra Luxury"

def load_style() -> None:
    if STYLE_PATH.exists():
        st.markdown(f"<style>{STYLE_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

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
    st.set_page_config(page_title="GrihaValue — Indian House Price Studio", page_icon="🏢", layout="wide")
    load_style()

    bundle = load_model_bundle()
    model = bundle["model"]
    city_locality_map = bundle["city_locality_map"]
    locality_coords = bundle["locality_coords"]
    
    try:
        property_types = bundle["property_types"]
        furnishing_options = bundle["furnishing_options"]
        status_options = bundle["status_options"]
    except KeyError as e:
        st.error(f"Model bundle is missing a required configuration key: {e}. Please re-train the model.")
        st.stop()
        
    showcase_df = pd.DataFrame(bundle.get("showcase_samples", []))

    st.markdown(
        """
        <header class="hero-shell">
          <div class="hero-left">
            <span class="hero-chip">Bharat Real Estate AI · 2026 Engine</span>
            <h1>GrihaValue — Indian House Price Predictor</h1>
            <p>Predict fair market valuations across India's top metropolitan hubs using machine learning trained on authentic ₹/sq.ft. transaction benchmarks.</p>
          </div>
          <div class="hero-right">
            <div class="hero-stat">
              <span>Cities Covered</span>
              <strong>7 Top Metros · 40+ Localities</strong>
            </div>
            <div class="hero-stat">
              <span>Model Accuracy</span>
              <strong>Random Forest Regressor (95.5% R²)</strong>
            </div>
          </div>
        </header>
        """,
        unsafe_allow_html=True,
    )

    section_header("Property Specifications", "Select your target city, micro-market, and residential parameters.")

    cities = list(city_locality_map.keys())

    if "selected_city" not in st.session_state:
        st.session_state["selected_city"] = DEFAULT_CITY

    col_city, col_loc = st.columns(2)
    with col_city:
        selected_city = st.selectbox(
            "Target Metropolitan City",
            options=cities,
            index=cities.index(st.session_state["selected_city"]) if st.session_state["selected_city"] in cities else 0,
            key="city_select"
        )
        st.session_state["selected_city"] = selected_city

    localities = city_locality_map.get(selected_city, [])
    with col_loc:
        selected_locality = st.selectbox(f"Locality in {selected_city}", options=localities, index=0, key="locality_select")

    loc_info = locality_coords.get(selected_locality)
    if not loc_info:
        st.error(f"Coordinates for locality '{selected_locality}' not found in the dataset.")
        st.stop()
        
    base_lat = loc_info["lat"]
    base_lon = loc_info["lon"]

    city_showcase = showcase_df[showcase_df["City"] == selected_city] if not showcase_df.empty else pd.DataFrame()
    city_prices = city_showcase["Price_INR"] if "Price_INR" in city_showcase.columns else pd.Series(dtype=float)
    
    def get_default_area(bhk: int) -> float:
        if not city_showcase.empty and "BHK" in city_showcase.columns and "Area_SqFt" in city_showcase.columns:
            bhk_data = city_showcase[city_showcase["BHK"] == bhk]
            if not bhk_data.empty:
                return float(bhk_data["Area_SqFt"].median())
        return float({1: 550.0, 2: 1100.0, 3: 1550.0, 4: 2600.0, 5: 3800.0}.get(bhk, 1500.0))

    with st.form("indian_house_features", border=False):
        st.subheader("Property Details")
        c1, c2, c3 = st.columns(3)

        with c1:
            bhk = st.slider("BHK Configuration", min_value=1, max_value=5, value=3, step=1)
            default_sqft = get_default_area(bhk)
            area_sqft = st.number_input("Super Built-up Area (sq. ft.)", min_value=100.0, max_value=10000.0, value=default_sqft, step=25.0)
            prop_type = st.selectbox("Property Type", options=property_types, index=0)

        with c2:
            bathrooms = st.slider("Bathrooms", min_value=1, max_value=6, value=max(1, bhk), step=1)
            furnishing = st.selectbox("Furnishing Status", options=furnishing_options, index=1)
            construction_status = st.selectbox("Possession Status", options=status_options, index=0)

        with c3:
            age_years = st.slider("Age of Property (Years)", min_value=0, max_value=25, value=2, step=1)
            parking = st.slider("Reserved Parking Spaces", min_value=0, max_value=3, value=1, step=1)
            locality_base = loc_info.get("base_rate", 8500)
            st.info(f"📍 **{selected_locality}** Benchmark:\n\n**₹{locality_base:,} / sq.ft.** indicative base rate")

        st.subheader("Financial Configuration")
        f1, f2, f3 = st.columns(3)
        with f1:
            user_downpayment_pct = st.slider("Down Payment (%)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
        with f2:
            user_rate = st.slider("Interest Rate (% p.a.)", min_value=float(FINANCE["rate_min"]), max_value=float(FINANCE["rate_max"]), value=float(FINANCE["default_rate_pct"]), step=0.1)
        with f3:
            user_tenure = st.slider("Loan Tenure (Years)", min_value=int(FINANCE["tenure_min"]), max_value=int(FINANCE["tenure_max"]), value=int(FINANCE["default_tenure_yrs"]), step=1)

        submitted = st.form_submit_button("Calculate Property Valuation", type="primary")

    # 1. Input Validation Guardrails
    warnings = []
    if area_sqft < bhk * 250:
        warnings.append("⚠️ The area seems unusually small for the selected BHK configuration.")
    if bathrooms > bhk + 2:
        warnings.append("⚠️ The number of bathrooms seems unusually high for this BHK.")
    if construction_status == "Under Construction" and age_years > 3:
        warnings.append("⚠️ An 'Under Construction' property is typically not this old.")
        
    for w in warnings:
        st.warning(w)

    if "first_run_done" not in st.session_state:
        submitted = True
        st.session_state["first_run_done"] = True

    if submitted or "latest_estimate" in st.session_state:
        input_data = {
            "City": [selected_city],
            "Locality": [selected_locality],
            "BHK": [bhk],
            "Area_SqFt": [area_sqft],
            "Bathrooms": [bathrooms],
            "Property_Type": [prop_type],
            "Furnishing": [furnishing],
            "Construction_Status": [construction_status],
            "Age_Years": [age_years],
            "Parking": [parking],
            "Latitude": [base_lat],
            "Longitude": [base_lon],
        }
        input_df = pd.DataFrame(input_data)
        predicted_price = float(model.predict(input_df)[0])
        rate_per_sqft = predicted_price / area_sqft
        tier = price_tier(predicted_price, city_prices)
        
        # 2. EMI Edge Cases & Downpayment Constraints
        max_ltv = calculate_ltv(predicted_price)
        min_required_downpayment = (1.0 - max_ltv) * 100
        
        if user_downpayment_pct < min_required_downpayment:
            st.error(f"❌ RBI caps loans for this property value at {int(max_ltv*100)}%. Your down payment must be at least {min_required_downpayment:.1f}%.")
            st.stop()
            
        loan_amount = predicted_price * (1.0 - (user_downpayment_pct / 100.0))
        monthly_emi = estimate_emi(loan_amount, user_rate, user_tenure)
        estimated_closing_costs = predicted_price * 0.07 # Assume 7% for stamp duty & registration

        st.session_state["latest_estimate"] = predicted_price

        section_header("Valuation Summary", f"Instant AI appraisal for {bhk} BHK {prop_type} in {selected_locality}, {selected_city}")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric(label="Estimated Market Value", value=format_inr(predicted_price), delta=f"₹{predicted_price:,.0f} Total", delta_color="off")
        m2.metric(label="Effective Rate / Sq.Ft.", value=f"₹{rate_per_sqft:,.0f}", delta=f"{((rate_per_sqft / loc_info.get('base_rate', rate_per_sqft)) - 1) * 100:+.1f}% vs locality base")
        m3.metric(label=f"Est. Monthly EMI", value=f"{format_inr(monthly_emi)}/mo", delta=f"{user_tenure} Yrs @ {user_rate}% p.a.", delta_color="off")
        m4.metric(label="Market Category", value=tier, delta=f"{construction_status}", delta_color="off")

        st.caption(f"💡 **Note:** Standard closing costs (Stamp Duty & Registration) will add approximately **{format_inr(estimated_closing_costs)}** (7%) to the total acquisition cost.")

        # 3. Enhanced Interactive Map Data
        section_header("Geographic Market Context", f"Location map centered on {selected_locality}, {selected_city}")
        
        view_state = pdk.ViewState(latitude=base_lat, longitude=base_lon, zoom=11, pitch=40)
        
        if not city_showcase.empty:
            map_samples = city_showcase.copy()
            map_samples["color"] = [[15, 82, 186, 160]] * len(map_samples) # Blue for showcase
            map_samples["radius"] = 300
            # Ensure price formatting for tooltip
            map_samples["FormattedPrice"] = map_samples["Price_INR"].apply(lambda x: format_inr(x) if pd.notnull(x) else "N/A")
        else:
            map_samples = pd.DataFrame([{"Latitude": base_lat, "Longitude": base_lon, "Locality": selected_locality, "BHK": bhk, "FormattedPrice": "N/A", "color": [15, 82, 186, 160], "radius": 300}])

        # The user's target property (Red pin)
        user_loc = pd.DataFrame([{"Latitude": base_lat, "Longitude": base_lon, "Locality": "Your Target Property", "BHK": bhk, "FormattedPrice": format_inr(predicted_price), "color": [220, 20, 60, 200], "radius": 500}])
        
        all_map_pts = pd.concat([map_samples, user_loc], ignore_index=True)
        
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=all_map_pts,
            get_position='[Longitude, Latitude]',
            get_color='color',
            get_radius='radius',
            pickable=True,
            auto_highlight=True
        )
        
        tooltip = {
            "html": "<b>{Locality}</b><br/>{BHK} BHK<br/>Price: {FormattedPrice}",
            "style": {"backgroundColor": "#06192f", "color": "white", "fontFamily": "Inter"}
        }
        
        r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)
        st.pydeck_chart(r)

        section_header("Scenario Sensitivity Analysis", "Explore how adjustments to area impact total valuation.")
        variations_pct = [-0.10, -0.05, 0.0, 0.05, 0.10]
        scenario_records = []
        for pct in variations_pct:
            scen_area = area_sqft * (1 + pct)
            row_copy = input_df.copy()
            row_copy["Area_SqFt"] = scen_area
            scen_pred = float(model.predict(row_copy)[0])
            label = "Current" if pct == 0 else f"{pct*100:+.0f}% Area"
            scenario_records.append({
                "Scenario": label,
                "Area (sq.ft)": f"{scen_area:,.0f}",
                "Estimated Price": scen_pred,
                "Price": format_inr(scen_pred),
                "Rate / sq.ft.": f"₹{scen_pred / scen_area:,.0f}"
            })
        scen_df = pd.DataFrame(scenario_records).set_index("Scenario")
        sc_col1, sc_col2 = st.columns([1.4, 1])
        with sc_col1:
            st.bar_chart(scen_df["Estimated Price"], color=ACCENT_COLOR)
        with sc_col2:
            st.dataframe(scen_df[["Area (sq.ft)", "Price", "Rate / sq.ft."]])

        # 4. Brittle Comparables Fallback Logic
        section_header("Real Market Comparables", "Similar properties from the historical dataset.")
        
        comps_found = False
        if not city_showcase.empty and "Locality" in city_showcase.columns and "BHK" in city_showcase.columns:
            # Attempt 1: Exact Match
            comps = city_showcase[(city_showcase["Locality"] == selected_locality) & (city_showcase["BHK"] == bhk)]
            match_type = "Exact Match"
            
            # Attempt 2: Similar BHK in same locality
            if comps.empty:
                comps = city_showcase[(city_showcase["Locality"] == selected_locality) & (city_showcase["BHK"].between(bhk-1, bhk+1))]
                match_type = "Similar Configuration"
                
            # Attempt 3: Similar price bracket in same city
            if comps.empty:
                price_min, price_max = predicted_price * 0.85, predicted_price * 1.15
                comps = city_showcase[city_showcase["Price_INR"].between(price_min, price_max)]
                match_type = "Similar Value (City-wide)"

            if not comps.empty:
                comps_found = True
                comps = comps.head(3)
                st.caption(f"🔍 Found via: {match_type}")
                l1, l2, l3 = st.columns(3)
                cols = [l1, l2, l3]
                for idx, (_, listing) in enumerate(comps.iterrows()):
                    if idx < 3:
                        with cols[idx]:
                            price_val = listing.get("Price_INR", 0)
                            sqft_val = listing.get("Area_SqFt", 0)
                            status_val = listing.get("Construction_Status", "Unknown")
                            bhk_val = listing.get("BHK", bhk)
                            loc_val = listing.get("Locality", selected_locality)
                            st.info(
                                f"**{bhk_val} BHK in {loc_val}**\n\n"
                                f"💰 {format_inr(price_val)}\n\n"
                                f"📏 {sqft_val:,.0f} sq.ft.\n\n"
                                f"🔑 {status_val}"
                            )

        if not comps_found:
            st.info("No historical comparables found matching this profile.")

        st.caption(f"⚡ Model Engine: {bundle.get('model_name', 'Random Forest')} | R² Evaluation: {bundle.get('r2_score', 0.95):.1%}")

if __name__ == "__main__":
    main()
