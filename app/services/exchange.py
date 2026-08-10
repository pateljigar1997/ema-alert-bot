import ccxt
import pandas as pd


exchange = ccxt.binance({
    "enableRateLimit": True
})


def get_ohlcv(symbol: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
    """
    Download OHLCV data from Binance
    """

    candles = exchange.fetch_ohlcv(
        symbol=symbol,
        timeframe=timeframe,
        limit=limit
    )

    df = pd.DataFrame(
        candles,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        unit="ms",
        utc=True
    )

    df = df.astype({
        "open": float,
        "high": float,
        "low": float,
        "close": float,
        "volume": float
    })

    return df