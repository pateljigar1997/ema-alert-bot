import pandas as pd


def calculate_emas(df: pd.DataFrame, fast_period: int, slow_period: int) -> pd.DataFrame:
    """
    Calculate Fast EMA and Slow EMA.
    """

    df = df.copy()

    df["ema_fast"] = (
        df["close"]
        .ewm(span=fast_period, adjust=False)
        .mean()
    )

    df["ema_slow"] = (
        df["close"]
        .ewm(span=slow_period, adjust=False)
        .mean()
    )

    return df