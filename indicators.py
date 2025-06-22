import requests
import pandas as pd
import numpy as np
from typing import Dict

BASE_URL = "https://api.bybit.com"
HEADERS = {"Content-Type": "application/json"}

TIMEFRAMES = {
    "5m": "5",
    "15m": "15",
    "30m": "30",
    "1h": "60",
    "2h": "120",
    "4h": "240",
    "1d": "D"
}

def get_candles(symbol: str, interval: str, limit: int = 200) -> pd.DataFrame:
    url = f"{BASE_URL}/v5/market/kline"
    params = {
        "category": "spot",
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    data = response.json()["result"]["list"]
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "turnover"])
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    return df.sort_values(by="timestamp")

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def stoch_rsi(series, period=14):
    rsi_series = rsi(series, period)
    min_val = rsi_series.rolling(window=14).min()
    max_val = rsi_series.rolling(window=14).max()
    stoch_k = (rsi_series - min_val) / (max_val - min_val)
    stoch_d = stoch_k.rolling(window=3).mean()
    return stoch_k, stoch_d

def compute_indicators_for_all_timeframes(symbol: str) -> Dict:
    result = {}
    for tf_name, interval in TIMEFRAMES.items():
        df = get_candles(symbol, interval)
        close = df["close"]

        ema_50 = ema(close, 50).iloc[-1]
        ema_200 = ema(close, 200).iloc[-1]
        rsi_val = rsi(close).iloc[-1]
        stoch_k, stoch_d = stoch_rsi(close)
        volume = df["volume"].iloc[-1]

        result[tf_name] = {
            "close": round(close.iloc[-1], 8),
            "ema_50": round(ema_50, 8),
            "ema_200": round(ema_200, 8),
            "rsi": round(rsi_val, 2),
            "stoch_rsi_k": round(stoch_k.iloc[-1], 2),
            "stoch_rsi_d": round(stoch_d.iloc[-1], 2),
            "volume": round(volume, 2)
        }
    return result
