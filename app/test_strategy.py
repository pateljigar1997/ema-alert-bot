from app.services.exchange import get_ohlcv
from app.indicators import calculate_ema
from app.strategies.ema_strategy import detect_cross


rule = {
    "direction": "both"
}

df = get_ohlcv(
    symbol="BTC/USDT",
    timeframe="15m"
)

df = calculate_ema(df, 51)

signal, candle = detect_cross(df, rule)

print("Signal :", signal)

print()

print(candle[["timestamp", "close", "ema"]])