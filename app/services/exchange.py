import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")

def get_ohlcv(symbol, timeframe, exchange="twelvedata", limit=200):
    """
    Fetch OHLCV data from Twelve Data.
    """

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

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    if "values" not in data:
        raise Exception(f"TwelveData Error: {data}")

    values = list(reversed(data["values"]))

    df = pd.DataFrame(values)

    df.rename(columns={"datetime": "timestamp"}, inplace=True)

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col])

    return df