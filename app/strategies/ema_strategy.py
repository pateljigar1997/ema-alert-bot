import pandas as pd


def detect_cross(df: pd.DataFrame, rule: dict):
    """
    Detect EMA21 / EMA51 crossover using the last two CLOSED candles.

    Returns:
        BUY / SELL / None
    """

    if len(df) < 3:
        return None, None

    # Last two CLOSED candles
    previous = df.iloc[-3]
    current = df.iloc[-2]

    previous_fast = previous["ema_fast"]
    previous_slow = previous["ema_slow"]

    current_fast = current["ema_fast"]
    current_slow = current["ema_slow"]

    bullish = (
        previous_fast <= previous_slow
        and current_fast > current_slow
    )

    bearish = (
        previous_fast >= previous_slow
        and current_fast < current_slow
    )

    if bullish:
        return "BUY", current

    if bearish:
        return "SELL", current

    return None, current