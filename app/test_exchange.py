from app.services.exchange import get_ohlcv

df = get_ohlcv(
    symbol="BTC/USDT",
    timeframe="15m"
)

print(df.tail())