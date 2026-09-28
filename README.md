# House Price Predictor

An intermediate machine-learning regression project that estimates California
house prices from neighborhood statistics, with a polished interactive web app.

## What makes it intermediate?

- Mixed numeric and categorical feature preprocessing
- Missing-value imputation and one-hot encoding
- Comparison of Ridge Regression and Random Forest
- Evaluation with MAE, RMSE, and R²
- Persisted model pipeline with Joblib
- Interactive Streamlit web app with custom styling, map preview, and scenario analysis

## Run it

```powershell
cd "$HOME\Downloads\house-price-predictor"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python train.py
streamlit run app.py
```

The first training run downloads the public California housing dataset through
scikit-learn. Keep the terminal open, then open the local URL shown by Streamlit.

## Web app highlights

- Premium light-first visual style with dark-mode support through system theme
- Slider-based control panel for quick experimentation
- Price estimate cards with baseline comparison
- Live map that plots your selected location
- Scenario impact chart that shows sensitivity to income changes
