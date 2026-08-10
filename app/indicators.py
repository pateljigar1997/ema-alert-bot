import pandas as pd


def calculate_ema(df: pd.DataFrame, period: int) -> pd.DataFrame:
    """
    Calculate EMA and append it to the dataframe.
    """

    df = df.copy()

    df["ema"] = (
        df["close"]
        .ewm(span=period, adjust=False)
        .mean()
    )

    return df