from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from typing import List



app = FastAPI()


# --- Ticker Resolution ---
# Maps common company names and shorthand to Yahoo Finance NSE tickers.
# Keys should be UPPERCASE.
TICKER_ALIASES = {
    # Company names -> NSE tickers
    "INFOSYS": "INFY.NS",
    "TATA CONSULTANCY": "TCS.NS",
    "TATA CONSULTANCY SERVICES": "TCS.NS",
    "RELIANCE": "RELIANCE.NS",
    "RELIANCE INDUSTRIES": "RELIANCE.NS",
    "HDFC BANK": "HDFCBANK.NS",
    "HDFC": "HDFCBANK.NS",
    "ICICI BANK": "ICICIBANK.NS",
    "ICICI": "ICICIBANK.NS",
    "WIPRO": "WIPRO.NS",
    "MARUTI": "MARUTI.NS",
    "MARUTI SUZUKI": "MARUTI.NS",
    "TATA MOTORS": "TATAMOTORS.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "TATA STEEL": "TATASTEEL.NS",
    "TATASTEEL": "TATASTEEL.NS",
    "SBI": "SBIN.NS",
    "STATE BANK": "SBIN.NS",
    "STATE BANK OF INDIA": "SBIN.NS",
    "SBIN": "SBIN.NS",
    "AXIS BANK": "AXISBANK.NS",
    "AXISBANK": "AXISBANK.NS",
    "KOTAK": "KOTAKBANK.NS",
    "KOTAK BANK": "KOTAKBANK.NS",
    "KOTAK MAHINDRA": "KOTAKBANK.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "BAJAJ FINANCE": "BAJFINANCE.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "HCL TECH": "HCLTECH.NS",
    "HCLTECH": "HCLTECH.NS",
    "HCL": "HCLTECH.NS",
    "HINDUSTAN UNILEVER": "HINDUNILVR.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "HUL": "HINDUNILVR.NS",
    "SUN PHARMA": "SUNPHARMA.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "TITAN": "TITAN.NS",
    "TECH MAHINDRA": "TECHM.NS",
    "TECHM": "TECHM.NS",
    "ADANI": "ADANIENT.NS",
    "ADANI ENTERPRISES": "ADANIENT.NS",
    "ADANIENT": "ADANIENT.NS",
    "LT": "LT.NS",
    "LARSEN": "LT.NS",
    "LARSEN AND TOUBRO": "LT.NS",
    "BHARTI AIRTEL": "BHARTIARTL.NS",
    "AIRTEL": "BHARTIARTL.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "ITC": "ITC.NS",
    "ASIAN PAINTS": "ASIANPAINT.NS",
    "ASIANPAINT": "ASIANPAINT.NS",
    "POWERGRID": "POWERGRID.NS",
    "NTPC": "NTPC.NS",
    "ONGC": "ONGC.NS",
    "COAL INDIA": "COALINDIA.NS",
    "COALINDIA": "COALINDIA.NS",
    "ULTRATECH": "ULTRACEMCO.NS",
    "ULTRACEMCO": "ULTRACEMCO.NS",
    "BAJAJ AUTO": "BAJAJ-AUTO.NS",
    "M&M": "M&M.NS",
    "MAHINDRA": "M&M.NS",
    "NESTLE": "NESTLEIND.NS",
    "NESTLEIND": "NESTLEIND.NS",
    "DIVIS LAB": "DIVISLAB.NS",
    "DIVISLAB": "DIVISLAB.NS",
    "DRREDDY": "DRREDDY.NS",
    "DR REDDY": "DRREDDY.NS",
    "CIPLA": "CIPLA.NS",
    "EICHER": "EICHERMOT.NS",
    "EICHER MOTORS": "EICHERMOT.NS",
    "EICHERMOT": "EICHERMOT.NS",
    "GRASIM": "GRASIM.NS",
    "HEROMOTOCO": "HEROMOTOCO.NS",
    "HERO": "HEROMOTOCO.NS",
    "HERO MOTOCORP": "HEROMOTOCO.NS",
    "HINDALCO": "HINDALCO.NS",
    "INDUSINDBK": "INDUSINDBK.NS",
    "INDUSIND BANK": "INDUSINDBK.NS",
    "JSWSTEEL": "JSWSTEEL.NS",
    "JSW STEEL": "JSWSTEEL.NS",
    "TATACONSUM": "TATACONSUM.NS",
    "TATA CONSUMER": "TATACONSUM.NS",
    "APOLLOHOSP": "APOLLOHOSP.NS",
    "APOLLO HOSPITAL": "APOLLOHOSP.NS",
    "APOLLO": "APOLLOHOSP.NS",
    "BRITANNIA": "BRITANNIA.NS",
    "SBILIFE": "SBILIFE.NS",
    "SBI LIFE": "SBILIFE.NS",
    "HDFCLIFE": "HDFCLIFE.NS",
    "HDFC LIFE": "HDFCLIFE.NS",
    "INFY": "INFY.NS",
    "TCS": "TCS.NS",
}


def resolve_ticker(raw_input: str) -> str:
    """
    Resolve user input to a valid Yahoo Finance NSE ticker.

    Handles:
      - Company names (e.g. "infosys" -> "INFY.NS")
      - Bare symbols (e.g. "INFY" -> "INFY.NS")
      - Already valid tickers (e.g. "INFY.NS" -> "INFY.NS")
    """
    cleaned = raw_input.strip().upper()

    # Already has .NS or .BO suffix — return as-is
    if cleaned.endswith(".NS") or cleaned.endswith(".BO"):
        return cleaned

    # Check alias map (company names and common shorthand)
    if cleaned in TICKER_ALIASES:
        return TICKER_ALIASES[cleaned]

    # Default: assume it's an NSE symbol and append .NS
    return cleaned + ".NS"


def _get_allowed_origins() -> List[str]:
    """Determine allowed CORS origins from environment.

    Read `ALLOWED_ORIGINS` (comma-separated) or `FRONTEND_URL`.
    Fall back to the local dev origin when not set.
    """
    raw = os.getenv("ALLOWED_ORIGINS") or os.getenv("FRONTEND_URL")
    if not raw:
        return ["http://localhost:5173"]
    return [o.strip() for o in raw.split(",") if o.strip()]


allowed_origins = _get_allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # Try to ensure models exist, but don't crash the app at import/startup
    try:
        from main import ensure_models_exist
    except Exception as e:
        print(f"Startup: could not import ensure_models_exist - {e}")
        return

    try:
        ensure_models_exist()
    except Exception as e:
        print(f"Startup: ensure_models_exist raised an exception - {e}")


@app.get("/api/predict/{ticker}")
def predict_stock(ticker: str):
    try:
        from main import analyze_stock
    except Exception as e:
        return {"error": "Server missing dependencies or failed to import analysis code.", "detail": str(e)}

    resolved = resolve_ticker(ticker)
    try:
        raw_result = analyze_stock(ticker=resolved, use_universal=True)
    except ValueError as e:
        return {"error": f"Could not find data for '{ticker}'. Try using the NSE ticker symbol (e.g., INFY.NS, TCS.NS, RELIANCE.NS).", "detail": str(e)}
    except Exception as e:
        return {"error": f"Analysis failed for '{ticker}'.", "detail": str(e)}
    
   
    formatted_prediction = "Bullish" if raw_result['prediction'] == 'UP' else "Bearish"
    
    formatted_shap = [
        {"feature": driver["feature"], "impact": driver["shap_value"]}
        for driver in raw_result['top_drivers']
    ]

    
    history_df = raw_result['price_history'].reset_index()
    chart_data = []
    for _, row in history_df.iterrows():
        chart_data.append({
            "time": row['Date'].strftime('%b %d'),
            "price": round(float(row['Close']), 2)
        })

    return {
        "ticker": raw_result['ticker'],
        "prediction": formatted_prediction,
        "probability": raw_result['probability_up'] if formatted_prediction == "Bullish" else raw_result['probability_down'],
        "risk_level": raw_result['risk_label'],
        "shap_values": formatted_shap,
        "current_price": f"₹{raw_result['close']:,.2f}",
        "price_change": "--", 
        "trend_data": chart_data 
    }


@app.get("/api/screener")
def get_screener_data():
   
    tickers = ["TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "WIPRO.NS", "MARUTI.NS"]
    screener_results = []

    for ticker in tickers:
        try:
            from main import analyze_stock
            res = analyze_stock(ticker, use_universal=True)
            screener_results.append({
                "ticker": res['ticker'],
                "price": f"₹{res['close']}",
                "prediction": "Bullish" if res['prediction'] == 'UP' else "Bearish",
                "probability": res['probability_up'] if res['prediction'] == 'UP' else res['probability_down'],
                "risk": res['risk_label']
            })
        except Exception as e:
            print(f"Error screening {ticker}: {e}")
            
    
    return sorted(screener_results, key=lambda x: x['probability'], reverse=True)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENV") == "development",
    )
