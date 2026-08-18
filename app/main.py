from app.config import load_config
from app.indicators import calculate_ema
from app.services.exchange import get_ohlcv
from app.services.logger import get_logger
from app.services.state import (
    load_state,
    save_state,
    is_duplicate,
    update_state,
    get_trend,
    update_trend,
)
from app.services.telegram_service import notify
from app.strategies.ema_strategy import detect_cross

logger = get_logger()


def main():
    logger.info("=" * 50)
    logger.info("XAU EMA Alert Bot Started")
    logger.info("=" * 50)

    config = load_config()
    state = load_state()

    logger.info(f"Loaded {len(config['rules'])} rule(s).")

    # =========================================================
    # 30M TREND CONFIRMATION
    # Price vs EMA51
    # =========================================================

    trend = get_trend(state)

    trend_rule = next(
        (
            rule
            for rule in config["rules"]
            if rule["enabled"] and rule["timeframe"] == "30m"
        ),
        None,
    )

    if trend_rule:
        try:
            logger.info("-" * 50)
            logger.info("Calculating 30m trend confirmation...")

            df_30m = get_ohlcv(
                symbol=trend_rule["symbol"],
                timeframe="30m",
                exchange=trend_rule["exchange"],
            )

            df_30m = calculate_ema(
                df_30m,
                51,
            )

            # Use latest CLOSED candle only.
            if len(df_30m) >= 2:

                candle_30m = df_30m.iloc[-2]

                price_30m = candle_30m["close"]
                ema_30m = candle_30m["ema"]
                timestamp_30m = str(candle_30m["timestamp"])

                # Determine current trend.
                if price_30m > ema_30m:
                    new_trend = "BULLISH"

                elif price_30m < ema_30m:
                    new_trend = "BEARISH"

                else:
                    new_trend = trend

                logger.info(
                    f"30m Price={price_30m:.2f} | "
                    f"EMA51={ema_30m:.2f}"
                )

                if new_trend:
                    trend = new_trend

                    update_trend(
                        state,
                        trend,
                        timestamp_30m,
                    )

                    save_state(state)

                    logger.info(
                        f"30m Trend: {trend}"
                    )

            else:
                logger.warning(
                    "Not enough 30m candle data."
                )

        except Exception as ex:
            logger.exception(ex)

    if trend is None:
        logger.warning(
            "No previous 30m trend available."
        )
    else:
        logger.info(
            f"Using 30m trend: {trend}"
        )

    # =========================================================
    # 5M + 15M SIGNALS
    # =========================================================

    for rule in config["rules"]:

        if not rule["enabled"]:
            continue

        # 30m is trend confirmation only.
        if rule["timeframe"] == "30m":
            continue

        logger.info("-" * 50)
        logger.info(f"Rule       : {rule['name']}")
        logger.info(f"Symbol     : {rule['symbol']}")
        logger.info(f"Timeframe  : {rule['timeframe']}")
        logger.info(f"EMA        : {rule['ema']}")

        try:
            df = get_ohlcv(
                symbol=rule["symbol"],
                timeframe=rule["timeframe"],
                exchange=rule["exchange"],
            )

            df = calculate_ema(
                df,
                rule["ema"],
            )

            signal, candle = detect_cross(
                df,
                rule,
            )

            if candle is None:
                logger.warning(
                    "No valid closed candle available."
                )
                continue

            logger.info(
                f"Price={candle['close']:.2f} | "
                f"EMA{rule['ema']}={candle['ema']:.2f}"
            )

            if signal is None:
                logger.info(
                    "No price/EMA crossover detected."
                )
                continue

            # =================================================
            # TREND CONFIRMATION
            # =================================================

            if trend is None:
                logger.info(
                    "Signal detected but 30m trend unavailable. "
                    "Skipping alert."
                )
                continue

            if signal == "BUY" and trend != "BULLISH":
                logger.info(
                    "BUY signal rejected: "
                    "30m trend is not bullish."
                )
                continue

            if signal == "SELL" and trend != "BEARISH":
                logger.info(
                    "SELL signal rejected: "
                    "30m trend is not bearish."
                )
                continue

            candle_timestamp = str(
                candle["timestamp"]
            )

            if is_duplicate(
                state,
                rule["id"],
                signal,
                candle_timestamp,
            ):
                logger.info(
                    "Duplicate signal. Skipping."
                )
                continue

            # =================================================
            # TELEGRAM ALERT
            # =================================================

            icon = (
                "🟢"
                if signal == "BUY"
                else "🔴"
            )

            direction_text = (
                f"Price crossed ABOVE EMA{rule['ema']}"
                if signal == "BUY"
                else f"Price crossed BELOW EMA{rule['ema']}"
            )

            trend_icon = (
                "🟢"
                if trend == "BULLISH"
                else "🔴"
            )

            message = (
                "🚨 XAU EMA CROSS ALERT 🚨\n\n"
                f"{icon} "
                f"{'BUY SIGNAL' if signal == 'BUY' else 'SELL SIGNAL'}\n\n"
                f"🪙 Symbol      : {rule['symbol']}\n"
                f"⏰ Timeframe   : {rule['timeframe']}\n"
                f"⚡ EMA         : EMA{rule['ema']}\n\n"
                f"📊 Price       : {candle['close']:.2f}\n"
                f"📈 EMA{rule['ema']}      : {candle['ema']:.2f}\n"
                f"🔔 Action      : {direction_text}\n\n"
                f"📌 30m Trend   : "
                f"{trend_icon} {trend}\n"
                f"📊 Trend EMA   : EMA51\n\n"
                f"🕒 Candle Close: {candle_timestamp}"
            )

            notify(message)

            logger.info(
                "Telegram sent."
            )

            update_state(
                state,
                rule["id"],
                signal,
                candle_timestamp,
            )

            save_state(state)

            logger.info(
                "State saved."
            )

        except Exception as ex:
            logger.exception(ex)

    logger.info("-" * 50)
    logger.info("Finished.")


if __name__ == "__main__":
    main()