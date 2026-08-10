import pandas as pd


def detect_cross(df: pd.DataFrame):
    previous = df.iloc[-2]
    current = df.iloc[-1]

    previous_above = previous["close"] > previous["ema"]
    current_above = current["close"] > current["ema"]

    if (not previous_above) and current_above:
        return "BULLISH"

    if previous_above and (not current_above):
        return "BEARISH"

    return None