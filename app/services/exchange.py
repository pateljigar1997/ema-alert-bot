import os
import requests
import ccxt
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")

binance = ccxt.binance({
    "enableRateLimit": True
})


def get_ohlcv(symbol, timeframe, exchange="binance", limit=200):

    if exchange.lower() == "binance":
        return get_binance_ohlcv(symbol, timeframe, limit)

    elif exchange.lower() == "twelvedata":
        return get_twelvedata_ohlcv(symbol, timeframe, limit)

    else:
        raise ValueError(f"Unsupported exchange: {exchange}")


def get_binance_ohlcv(symbol, timeframe, limit=200):

    ohlcv = binance.fetch_ohlcv(
        symbol=symbol,
        timeframe=timeframe,
        limit=limit
    )

    df = pd.DataFrame(
        ohlcv,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    )

    return df


def get_twelvedata_ohlcv(symbol, timeframe, limit=200):

    interval_map = {
        "5m": "5min",
        "15m": "15min",
        "30m": "30min"
    }

    url = "https://api.twelvedata.com/time_series"

    params = {
        "symbol": symbol,
        "interval": interval_map[timeframe],
        "outputsize": limit,
        "apikey": TWELVEDATA_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "values" not in data:
        raise Exception(data)

    values = list(reversed(data["values"]))

    df = pd.DataFrame(values)

    df = df.rename(columns={
        "datetime": "timestamp"
    })

    numeric_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(float)

    return df