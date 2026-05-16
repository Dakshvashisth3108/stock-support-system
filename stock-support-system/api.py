from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from typing import List



app = FastAPI()


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

    raw_result = analyze_stock(ticker=ticker.upper(), use_universal=True)
    
   
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
