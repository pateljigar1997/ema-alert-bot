import pandas as pd


def detect_cross(df: pd.DataFrame, rule: dict):
    """
    Detect EMA crossover using the last two CLOSED candles.

    Returns:
        signal : BUY | SELL | None
        candle : Closed candle (current)
    """

    if len(df) < 3:
        return None, None

    # Last two CLOSED candles
    previous = df.iloc[-3]
    current = df.iloc[-2]

    previous_above = previous["close"] > previous["ema"]
    current_above = current["close"] > current["ema"]

    bullish = (not previous_above) and current_above
    bearish = previous_above and (not current_above)

    direction = rule["direction"].lower()

    if bullish and direction in ["above", "both"]:
        return "BUY", current

    if bearish and direction in ["below", "both"]:
        return "SELL", current

    return None, current