"""Train a realistic house-price regression model for the Indian residential market."""

from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_DIR = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_DIR / "indian_house_price_model.joblib"

# Benchmarked Indian Metro Cities and Micro-Markets
LOCALITY_DATA = {
    "Bengaluru": [
        {"locality": "Whitefield", "base_rate": 8800, "lat": 12.9698, "lon": 77.7500},
        {"locality": "Indiranagar", "base_rate": 16500, "lat": 12.9784, "lon": 77.6408},
        {"locality": "Koramangala", "base_rate": 15200, "lat": 12.9352, "lon": 77.6245},
        {"locality": "HSR Layout", "base_rate": 11800, "lat": 12.9121, "lon": 77.6446},
        {"locality": "Electronic City", "base_rate": 6900, "lat": 12.8399, "lon": 77.6770},
        {"locality": "Bellandur / ORR", "base_rate": 10500, "lat": 12.9304, "lon": 77.6784},
        {"locality": "Hebbal", "base_rate": 11200, "lat": 13.0358, "lon": 77.5970},
        {"locality": "Sarjapur Road", "base_rate": 8400, "lat": 12.8600, "lon": 77.7400},
    ],
    "Mumbai (MMR)": [
        {"locality": "Bandra West", "base_rate": 46000, "lat": 19.0596, "lon": 72.8295},
        {"locality": "Andheri West", "base_rate": 26500, "lat": 19.1197, "lon": 72.8468},
        {"locality": "Powai", "base_rate": 23000, "lat": 19.1176, "lon": 72.9060},
        {"locality": "Worli / South Mumbai", "base_rate": 43500, "lat": 19.0178, "lon": 72.8178},
        {"locality": "Thane West", "base_rate": 13800, "lat": 19.2183, "lon": 72.9781},
        {"locality": "Navi Mumbai (Vashi/Nerul)", "base_rate": 12500, "lat": 19.0330, "lon": 73.0297},
        {"locality": "Borivali West", "base_rate": 18900, "lat": 19.2307, "lon": 72.8567},
    ],
    "Delhi NCR": [
        {"locality": "Gurgaon - Golf Course Rd", "base_rate": 24500, "lat": 28.4595, "lon": 77.0266},
        {"locality": "Gurgaon - Cyber City / DLF", "base_rate": 17800, "lat": 28.4900, "lon": 77.0800},
        {"locality": "Gurgaon - Sohna Road", "base_rate": 11200, "lat": 28.4000, "lon": 77.0400},
        {"locality": "Noida - Sector 62", "base_rate": 9500, "lat": 28.6250, "lon": 77.3650},
        {"locality": "Noida Expressway", "base_rate": 10800, "lat": 28.5100, "lon": 77.4000},
        {"locality": "Greater Noida", "base_rate": 6800, "lat": 28.4744, "lon": 77.5040},
        {"locality": "South Delhi - GK / Saket", "base_rate": 33000, "lat": 28.5432, "lon": 77.2427},
    ],
    "Hyderabad": [
        {"locality": "Hitec City", "base_rate": 11800, "lat": 17.4435, "lon": 78.3772},
        {"locality": "Gachibowli", "base_rate": 10600, "lat": 17.4401, "lon": 78.3489},
        {"locality": "Madhapur", "base_rate": 11200, "lat": 17.4483, "lon": 78.3915},
        {"locality": "Jubilee Hills", "base_rate": 19500, "lat": 17.4319, "lon": 78.4073},
        {"locality": "Kondapur", "base_rate": 8900, "lat": 17.4699, "lon": 78.3578},
        {"locality": "Miyapur", "base_rate": 6500, "lat": 17.4968, "lon": 78.3548},
    ],
    "Pune": [
        {"locality": "Hinjewadi", "base_rate": 7800, "lat": 18.5913, "lon": 73.7389},
        {"locality": "Wakad", "base_rate": 8400, "lat": 18.5987, "lon": 73.7667},
        {"locality": "Baner", "base_rate": 10800, "lat": 18.5590, "lon": 73.7868},
        {"locality": "Kothrud", "base_rate": 12400, "lat": 18.5074, "lon": 73.8077},
        {"locality": "Viman Nagar", "base_rate": 11500, "lat": 18.5679, "lon": 73.9143},
        {"locality": "Kharadi", "base_rate": 9100, "lat": 18.5514, "lon": 73.9348},
    ],
    "Chennai": [
        {"locality": "OMR - IT Corridor", "base_rate": 7700, "lat": 12.9346, "lon": 80.2312},
        {"locality": "Velachery", "base_rate": 9400, "lat": 12.9791, "lon": 80.2185},
        {"locality": "Adyar", "base_rate": 16800, "lat": 13.0012, "lon": 80.2565},
        {"locality": "Anna Nagar", "base_rate": 14200, "lat": 13.0850, "lon": 80.2101},
        {"locality": "Porur", "base_rate": 7000, "lat": 13.0382, "lon": 80.1565},
    ],
    "Kolkata": [
        {"locality": "New Town", "base_rate": 6900, "lat": 22.5851, "lon": 88.4798},
        {"locality": "Salt Lake", "base_rate": 9800, "lat": 22.5867, "lon": 88.4178},
        {"locality": "Ballygunge", "base_rate": 14500, "lat": 22.5280, "lon": 88.3655},
        {"locality": "Rajarhat", "base_rate": 5800, "lat": 22.6179, "lon": 88.4862},
    ]
}

PROPERTY_TYPE_MULTIPLIER = {
    "Apartment": 1.0,
    "Builder Floor": 1.08,
    "Independent Villa": 1.35,
    "Penthouse": 1.45,
}

FURNISHING_MULTIPLIER = {
    "Unfurnished": 1.0,
    "Semi-Furnished": 1.06,
    "Fully Furnished": 1.15,
}

STATUS_MULTIPLIER = {
    "Ready to Move": 1.05,
    "Under Construction": 0.94,
}

def generate_indian_housing_dataset(n_samples: int = 12000, random_state: int = 42) -> pd.DataFrame:
    """Generate realistic property data modeled on Indian Tier-1 market transactions."""
    rng = np.random.default_rng(random_state)
    records = []

    all_localities = []
    for city, loc_list in LOCALITY_DATA.items():
        for loc in loc_list:
            all_localities.append({"city": city, **loc})

    bhk_distribution = [1, 2, 3, 4, 5]
    bhk_weights = [0.12, 0.44, 0.32, 0.09, 0.03]

    for _ in range(n_samples):
        loc_choice = rng.choice(all_localities)
        city = loc_choice["city"]
        locality = loc_choice["locality"]
        base_rate = loc_choice["base_rate"]
        lat = loc_choice["lat"] + rng.normal(0, 0.015)
        lon = loc_choice["lon"] + rng.normal(0, 0.015)

        bhk = int(rng.choice(bhk_distribution, p=bhk_weights))

        # Typical sqft ranges by BHK in Indian metropolitan cities
        if bhk == 1:
            sqft = float(rng.uniform(420, 680))
            baths = 1
        elif bhk == 2:
            sqft = float(rng.uniform(850, 1350))
            baths = rng.choice([2, 1], p=[0.85, 0.15])
        elif bhk == 3:
            sqft = float(rng.uniform(1400, 2150))
            baths = rng.choice([3, 2, 4], p=[0.75, 0.20, 0.05])
        elif bhk == 4:
            sqft = float(rng.uniform(2200, 3600))
            baths = rng.choice([4, 3, 5], p=[0.75, 0.15, 0.10])
        else: # 5 BHK
            sqft = float(rng.uniform(3400, 5600))
            baths = rng.choice([5, 4, 6], p=[0.70, 0.20, 0.10])

        sqft = round(sqft, -1)

        prop_type = rng.choice(["Apartment", "Builder Floor", "Independent Villa", "Penthouse"], p=[0.72, 0.14, 0.11, 0.03])
        furnishing = rng.choice(["Unfurnished", "Semi-Furnished", "Fully Furnished"], p=[0.30, 0.52, 0.18])
        status = rng.choice(["Ready to Move", "Under Construction"], p=[0.70, 0.30])
        age = int(rng.choice([0, 1, 2, 4, 7, 12, 18], p=[0.25, 0.20, 0.18, 0.15, 0.12, 0.07, 0.03]))
        parking = int(rng.choice([1, 2, 0], p=[0.65, 0.25, 0.10]))

        # Rate calculations with market realities
        eff_rate = base_rate * PROPERTY_TYPE_MULTIPLIER[prop_type] * FURNISHING_MULTIPLIER[furnishing] * STATUS_MULTIPLIER[status]
        # Age depreciation: slight decrease for older properties (up to ~15% for 15+ years)
        age_factor = max(0.85, 1.0 - (age * 0.009))
        eff_rate = eff_rate * age_factor

        # Add realistic noise/variance (±6%)
        noise = rng.normal(1.0, 0.055)
        eff_rate = eff_rate * noise

        total_price = round(eff_rate * sqft, -3)

        records.append({
            "City": city,
            "Locality": locality,
            "BHK": bhk,
            "Area_SqFt": sqft,
            "Bathrooms": baths,
            "Property_Type": prop_type,
            "Furnishing": furnishing,
            "Construction_Status": status,
            "Age_Years": age,
            "Parking": parking,
            "Latitude": lat,
            "Longitude": lon,
            "Price_INR": total_price,
            "Rate_Per_SqFt": round(total_price / sqft, 1)
        })

    return pd.DataFrame(records)

def build_model_pipeline(numeric_features: list[str], categorical_features: list[str]) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
        ]
    )
    rf = RandomForestRegressor(
        n_estimators=160,
        max_depth=16,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    model = TransformedTargetRegressor(regressor=rf, func=np.log1p, inverse_func=np.expm1)
    return Pipeline([("preprocessor", preprocessor), ("model", model)])

def main():
    print("Generating calibrated Indian real estate dataset...")
    df = generate_indian_housing_dataset(n_samples=14000)

    numeric_features = ["BHK", "Area_SqFt", "Bathrooms", "Age_Years", "Parking", "Latitude", "Longitude"]
    categorical_features = ["City", "Locality", "Property_Type", "Furnishing", "Construction_Status"]

    features = df[numeric_features + categorical_features]
    target = df["Price_INR"]

    x_train, x_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

    pipeline = build_model_pipeline(numeric_features, categorical_features)
    print("Training Random Forest Regressor on Indian Housing transactions...")
    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    r2 = r2_score(y_test, predictions)

    print(f"Model Evaluation on Test Split:")
    print(f"  R² Score: {r2:.4f}")
    print(f"  MAE: INR {mae:,.0f} ({mae / 100000:.2f} Lakhs)")
    print(f"  RMSE: INR {rmse:,.0f} ({rmse / 100000:.2f} Lakhs)")

    # Full fit on entire dataset
    print("Fitting model across full dataset...")
    pipeline.fit(features, target)

    # City to localities mapping
    city_locality_map = {}
    locality_coords = {}
    for city, loc_list in LOCALITY_DATA.items():
        city_locality_map[city] = [loc["locality"] for loc in loc_list]
        for loc in loc_list:
            locality_coords[loc["locality"]] = {"lat": loc["lat"], "lon": loc["lon"], "base_rate": loc["base_rate"]}

    # Sample showcase points for map
    showcase_samples = df.sample(n=3000, random_state=42)[
        ["City", "Locality", "BHK", "Area_SqFt", "Price_INR", "Latitude", "Longitude", "Construction_Status", "Property_Type"]
    ].to_dict(orient="records")

    feature_defaults = {
        "City": "Bengaluru",
        "Locality": "Whitefield",
        "BHK": 3,
        "Area_SqFt": 1550.0,
        "Bathrooms": 3,
        "Property_Type": "Apartment",
        "Furnishing": "Semi-Furnished",
        "Construction_Status": "Ready to Move",
        "Age_Years": 2,
        "Parking": 1,
        "Latitude": 12.9698,
        "Longitude": 77.7500,
    }

    bundle = {
        "model": pipeline,
        "model_name": "Random Forest Regressor (India Edition)",
        "r2_score": r2,
        "mae_lakhs": mae / 100000,
        "feature_defaults": feature_defaults,
        "city_locality_map": city_locality_map,
        "locality_coords": locality_coords,
        "showcase_samples": showcase_samples,
        "property_types": list(PROPERTY_TYPE_MULTIPLIER.keys()),
        "furnishing_options": list(FURNISHING_MULTIPLIER.keys()),
        "status_options": list(STATUS_MULTIPLIER.keys()),
    }

    joblib.dump(bundle, MODEL_PATH)
    print(f"Successfully saved trained Indian housing model to {MODEL_PATH}")

if __name__ == "__main__":
    main()
