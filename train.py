"""Train a house-price regression model on the California housing dataset."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_DIR = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_DIR / "house_price_model.joblib"


def load_data() -> tuple[pd.DataFrame, pd.Series]:
    """Load the public California housing dataset and add a useful category."""
    dataset = fetch_california_housing(as_frame=True)
    features = dataset.data.copy()
    target = dataset.target * 100_000
    features["income_band"] = pd.cut(
        features["MedInc"],
        bins=[0, 3, 5, 8, float("inf")],
        labels=["Low", "Medium", "High", "Very high"],
    ).astype("object")
    return features, target


def build_preprocessor(
    numeric_features: list[str], categorical_features: list[str]
) -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        [
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ]
    )


def main() -> None:
    features, target = load_data()
    numeric_features = features.select_dtypes(include="number").columns.tolist()
    categorical_features = features.select_dtypes(exclude="number").columns.tolist()
    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42
    )

    preprocessor = build_preprocessor(numeric_features, categorical_features)
    candidates = {
        "Ridge": Ridge(alpha=10.0),
        "Random Forest": RandomForestRegressor(
            n_estimators=150, max_depth=18, min_samples_leaf=2,
            random_state=42, n_jobs=-1
        ),
    }
    results = {}
    for name, estimator in candidates.items():
        pipeline = Pipeline([("preprocessor", preprocessor), ("model", estimator)])
        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)
        results[name] = {
            "mae": mean_absolute_error(y_test, predictions),
            "rmse": mean_squared_error(y_test, predictions) ** 0.5,
            "r2": r2_score(y_test, predictions),
        }
        print(
            f"{name}: MAE=${results[name]['mae']:,.0f}, "
            f"RMSE=${results[name]['rmse']:,.0f}, R²={results[name]['r2']:.3f}"
        )

    best_name = max(results, key=lambda name: results[name]["r2"])
    best_model = Pipeline(
        [("preprocessor", preprocessor), ("model", candidates[best_name])]
    )
    best_model.fit(features, target)
    joblib.dump(
        {
            "model": best_model,
            "model_name": best_name,
            "feature_defaults": features.median(numeric_only=True).to_dict(),
            "feature_ranges": {
                column: {
                    "min": float(features[column].quantile(0.01)),
                    "max": float(features[column].quantile(0.99)),
                }
                for column in numeric_features
            },
            "showcase_samples": features.sample(n=180, random_state=42)[
                ["Latitude", "Longitude", "MedInc", "HouseAge"]
            ].to_dict(orient="records"),
            "categorical_values": {
                "income_band": ["Low", "Medium", "High", "Very high"]
            },
        },
        MODEL_PATH,
    )
    print(f"Selected {best_name}; saved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
