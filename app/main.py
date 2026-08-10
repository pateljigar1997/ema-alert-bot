from app.config import load_config
from app.indicators import calculate_ema
from app.services.exchange import get_ohlcv
from app.services.logger import get_logger
from app.services.state import load_state, save_state
from app.services.telegram_service import notify
from app.strategies.ema_strategy import detect_cross

logger = get_logger()


def main():

    logger.info("========================================")
    logger.info("EMA Alert Bot Started")
    logger.info("========================================")

    config = load_config()
    state = load_state()

    logger.info(f"Loaded {len(config['rules'])} rule(s).")

    for rule in config["rules"]:

        if not rule["enabled"]:
            logger.info(f"Skipping disabled rule: {rule['name']}")
            continue

        logger.info("----------------------------------------")
        logger.info(f"Checking : {rule['name']}")
        logger.info(f"Symbol   : {rule['symbol']}")
        logger.info(f"TF       : {rule['timeframe']}")
        logger.info(f"EMA      : {rule['ema']}")

        try:

            # Download candles
            df = get_ohlcv(
                symbol=rule["symbol"],
                timeframe=rule["timeframe"]
            )

            # Calculate EMA
            df = calculate_ema(df, rule["ema"])

            # Detect signal
            signal, candle = detect_cross(df, rule)

            if candle is None:
                logger.warning("Not enough candles.")
                continue

            logger.info(
                f"Close={candle['close']:.2f} | EMA={candle['ema']:.2f}"
            )

            if signal is None:
                logger.info("No EMA crossover.")
                continue

            candle_time = str(candle["timestamp"])

            previous = state.get(rule["id"])

            if (
                previous
                and previous["timestamp"] == candle_time
                and previous["signal"] == signal
            ):
                logger.info("Duplicate signal. Skipping.")
                continue

            icon = "🟢" if signal == "BUY" else "🔴"

            message = f"""
🚨 EMA CROSS ALERT

{icon} {signal}

🪙 Symbol
{rule['symbol']}

⏰ Timeframe
{rule['timeframe']}

📈 EMA
{rule['ema']}

━━━━━━━━━━━━━━

💰 Close
{candle['close']:.2f}

📉 EMA
{candle['ema']:.2f}

━━━━━━━━━━━━━━

🕒 Candle

{candle['timestamp']}
"""

            logger.info("Sending Telegram alert...")

            notify(message)

            logger.info("Telegram sent successfully.")

            state[rule["id"]] = {
                "signal": signal,
                "timestamp": candle_time
            }

            save_state(state)

            logger.info("State updated.")

        except Exception as ex:
            logger.exception(ex)

    logger.info("----------------------------------------")
    logger.info("Finished.")


if __name__ == "__main__":
    main()