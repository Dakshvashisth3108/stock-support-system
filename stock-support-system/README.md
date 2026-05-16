# AI-Powered Stock Decision Support System

A machine learning system that analyzes historical stock data to provide
probabilistic insights, risk evaluation, and explainable signals for better
investment decisions.

## What it does

- Fetches 10 years of historical data for any NSE stock
- Engineers 75+ technical, momentum, volatility, and market context features
- Trains an ensemble of Random Forest + XGBoost on 15 stocks simultaneously
- Outputs probability of price direction, risk level, and SHAP explanations

## Results

- 52.3% average accuracy across 5-year walk-forward validation
- Beats buy-and-hold during bear markets with strict confidence filtering
- Works on any NSE stock ticker

## Tech Stack

Python, FastAPI, Pandas, NumPy, scikit-learn, XGBoost, SHAP, yfinance

## Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/dakshvashisth3108/stock-support-system.git
cd stock-support-system/stock-support-system
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Train the universal model

```bash
python src/universal_model.py
```

### 5. Run the API

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

### 6. Run analysis on any stock

```bash
python main.py TCS.NS
python main.py RELIANCE.NS
python main.py SUNPHARMA.NS
```

## Deployment

### Render backend

- Root Directory: `stock-support-system`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- Environment Variable: `ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app`

### Vercel frontend

- Root Directory: `frontend`
- Framework Preset: Vite
- Build Command: `npm run build`
- Output Directory: `dist`
- Environment Variable: `VITE_API_BASE_URL=https://your-render-service.onrender.com`

## Project Structure

```text
src/
  data_pipeline.py     # Data fetching and validation
  features.py          # Feature engineering
  targets.py           # Target variable creation
  model.py             # Random Forest + XGBoost training
  universal_model.py   # Multi-stock universal model
  walk_forward.py      # Walk-forward validation
  backtest.py          # Backtesting engine
  risk.py              # Risk scoring
  explainability.py    # SHAP explainability
  feature_selection.py # SHAP-based feature selection
  tuning.py            # Hyperparameter tuning
api.py                 # FastAPI app
main.py                # CLI analysis entry point
```

## Important Note

Models and data are not included in this repo because they are large. Run
`python src/universal_model.py` to train from scratch before production
prediction traffic, or provide model artifacts through persistent storage.
