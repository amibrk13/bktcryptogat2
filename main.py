from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from indicators import compute_indicators_for_all_timeframes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/analyze/{symbol}")
async def analyze_symbol(symbol: str):
    symbol = symbol.upper()
    try:
        result = compute_indicators_for_all_timeframes(symbol)
        return {"symbol": symbol, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
