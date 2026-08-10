from app.config import load_config
from app.indicators import calculate_emas
from app.services.exchange import get_ohlcv
from app.services.logger import get_logger
from app.services.state import (
    load_state,
    save_state,
    is_duplicate,
    update_state,
)
from app.services.telegram_service import notify
from app.strategies.ema_strategy import detect_cross

logger = get_logger()


def main():
    logger.info("=" * 50)
    logger.info("EMA Cross Alert Bot Started")
    logger.info("=" * 50)

    config = load_config()
    state = load_state()

    logger.info(f"Loaded {len(config['rules'])} rule(s).")

    for rule in config["rules"]:

        if not rule["enabled"]:
            continue

        logger.info("-" * 50)
        logger.info(f"Rule       : {rule['name']}")
        logger.info(f"Symbol     : {rule['symbol']}")
        logger.info(f"Timeframe  : {rule['timeframe']}")
        logger.info(f"Fast EMA   : {rule['fast_ema']}")
        logger.info(f"Slow EMA   : {rule['slow_ema']}")

        try:

            df = get_ohlcv(
    symbol=rule["symbol"],
    timeframe=rule["timeframe"],
    exchange=rule["exchange"],
)

            df = calculate_emas(
                df,
                rule["fast_ema"],
                rule["slow_ema"],
            )

            signal, candle = detect_cross(df, rule)

            if candle is None:
                logger.warning("Not enough candle data.")
                continue

            logger.info(
                f"EMA21={candle['ema_fast']:.2f} | EMA51={candle['ema_slow']:.2f}"
            )

            if signal is None:
                logger.info("No crossover detected.")
                continue

            candle_timestamp = str(candle["timestamp"])

            if is_duplicate(
                state,
                rule["id"],
                signal,
                candle_timestamp,
            ):
                logger.info("Duplicate signal. Skipping.")
                continue

            icon = "🟢" if signal == "BUY" else "🔴"

            message = (
    "🚨 EMA CROSS ALERT 🚨\n\n"
    f"{'🟢 BUY SIGNAL' if signal == 'BUY' else '🔴 SELL SIGNAL'}\n\n"
    f"🪙 Symbol      : {rule['symbol']}\n"
    f"⏰ Timeframe   : {rule['timeframe']}\n"
    f"📊 Strategy    : EMA {rule['fast_ema']} / EMA {rule['slow_ema']}\n\n"
    f"{f'📈 EMA {rule['fast_ema']} crossed ABOVE EMA {rule['slow_ema']}' if signal == 'BUY' else f'📉 EMA {rule["fast_ema"]} crossed BELOW EMA {rule["slow_ema"]}'}\n\n"
    f"⚡ EMA {rule['fast_ema']} : {candle['ema_fast']:.2f}\n"
    f"⚡ EMA {rule['slow_ema']} : {candle['ema_slow']:.2f}\n\n"
    f"🕒 Candle Close : {candle_timestamp}"
)

            notify(message)

            logger.info("Telegram sent.")

            update_state(
                state,
                rule["id"],
                signal,
                candle_timestamp,
            )

            save_state(state)

            logger.info("State saved.")

        except Exception as ex:
            logger.exception(ex)

    logger.info("-" * 50)
    logger.info("Finished.")


if __name__ == "__main__":
    main()