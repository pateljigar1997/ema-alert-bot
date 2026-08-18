import pandas as pd


def detect_cross(df: pd.DataFrame, rule: dict):
    """
    Detect Price/EMA crossover using CLOSED candles only.

    BUY:
        Previous closed candle was at/below EMA
        Current closed candle is above EMA

    SELL:
        Previous closed candle was at/above EMA
        Current closed candle is below EMA

    The latest candle is treated as the currently forming candle.
    Weekend candles are ignored.
    """

    if len(df) < 3:
        return None, None

    # ---------------------------------------------------------
    # Candle selection
    #
    # -3 = previous CLOSED candle
    # -2 = latest CLOSED candle
    # -1 = current/forming candle
    # ---------------------------------------------------------

    previous = df.iloc[-3]
    current = df.iloc[-2]

    # ---------------------------------------------------------
    # Timestamp
    # ---------------------------------------------------------

    candle_timestamp = pd.to_datetime(
        current["timestamp"],
        utc=True,
    )

    # Ignore Saturday / Sunday.
    if candle_timestamp.weekday() >= 5:
        return None, None

    # ---------------------------------------------------------
    # Price vs EMA
    # ---------------------------------------------------------

    previous_price = float(previous["close"])
    previous_ema = float(previous["ema"])

    current_price = float(current["close"])
    current_ema = float(current["ema"])

    # ---------------------------------------------------------
    # BUY
    # Price crossed ABOVE EMA
    # ---------------------------------------------------------

    bullish = (
        previous_price <= previous_ema
        and current_price > current_ema
    )

    if bullish:
        return "BUY", current

    # ---------------------------------------------------------
    # SELL
    # Price crossed BELOW EMA
    # ---------------------------------------------------------

    bearish = (
        previous_price >= previous_ema
        and current_price < current_ema
    )

    if bearish:
        return "SELL", current

    return None, current