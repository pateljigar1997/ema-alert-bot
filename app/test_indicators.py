from app.services.exchange import get_ohlcv
from app.indicators import calculate_ema

df = get_ohlcv(
    symbol="BTC/USDT",
    timeframe="15m"
)

df = calculate_ema(df, 51)

print(df[["timestamp", "close", "ema"]].tail())