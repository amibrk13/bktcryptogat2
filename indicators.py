import requests
import pandas as pd
import numpy as np
import ta
import time

# Таймфреймы и соответствующие интервалы Bybit
TIMEFRAMES = {
    "5m": "5",
    "15m": "15",
    "30m": "30",
    "1h": "60",
    "2h": "120",
    "4h": "240",
    "1d": "D"
}

# Получение исторических данных с Bybit Spot API
def fetch_ohlcv(symbol: str, interval: str, limit: int = 200):
    url = "https://api.bybit.com/v5/market/kline"
    params = {
        "category": "spot",
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "result" not in data or "list" not in data["result"]:
        raise ValueError(f"Invalid response from Bybit for interval {interval}")
    ohlcv = pd.DataFrame(data["result"]["list"])
    ohlcv.columns = ["timestamp", "open", "high", "low", "close", "volume", "_"]
    ohlcv = ohlcv[["timestamp", "open", "high", "low", "close", "volume"]]
    ohlcv = ohlcv.astype(float)
    ohlcv["timestamp"] = pd.to_datetime(ohlcv["timestamp"], unit="ms")
    ohlcv = ohlcv.sort_values("timestamp").reset_index(drop=True)
    return ohlcv

# Расчёт индикаторов на основе OHLCV
def compute_indicators(df):
    close = df["close"]
    volume = df["volume"]

    ema_50 = ta.trend.ema_indicator(close, window=50).iloc[-1]
    ema_200 = ta.trend.ema_indicator(close, window=200).iloc[-1]
    rsi = ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1]

    stoch_rsi = ta.momentum.StochRSIIndicator(close, window=14, smooth1=3, smooth2=3)
    stoch_k = stoch_rsi.stochrsi_k().iloc[-1]
    stoch_d = stoch_rsi.stochrsi_d().iloc[-1]

    return {
        "close": round(close.iloc[-1], 2),
        "ema_50": round(ema_50, 2),
        "ema_200": round(ema_200, 2),
        "rsi": round(rsi, 2),
        "stoch_rsi_k": round(stoch_k, 2),
        "stoch_rsi_d": round(stoch_d, 2),
        "volume": round(volume.iloc[-1], 2)
    }

# Главная функция: анализ по всем таймфреймам
def compute_indicators_for_all_timeframes(symbol: str):
    result = {}
    for name, interval in TIMEFRAMES.items():
        print(f"Fetching {symbol} data for {name} timeframe...")
        df = fetch_ohlcv(symbol, interval)
        result[name] = compute_indicators(df)
        time.sleep(1)  # ⏳ Пауза между запросами, чтобы API не баговал
    return result
