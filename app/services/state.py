import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
STATE_FILE = DATA_DIR / "state.json"


def load_state() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not STATE_FILE.exists():
        save_state({})
        return {}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def save_state(state: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(
            state,
            file,
            indent=4,
            ensure_ascii=False
        )


def is_duplicate(state: dict, rule_id: str, signal: str, timestamp: str) -> bool:
    """
    Returns True if the same signal has already been sent
    for the same candle.
    """

    previous = state.get(rule_id)

    if previous is None:
        return False

    return (
        previous.get("signal") == signal
        and previous.get("timestamp") == timestamp
    )


def update_state(state: dict, rule_id: str, signal: str, timestamp: str) -> None:
    """
    Update state after sending Telegram alert.
    """

    state[rule_id] = {
        "signal": signal,
        "timestamp": timestamp
    }


def get_trend(state: dict):
    """
    Return the last stored 30m trend.
    """

    trend_state = state.get("gold-30m-trend")

    if trend_state is None:
        return None

    return trend_state.get("trend")


def update_trend(state: dict, trend: str, timestamp: str) -> None:
    """
    Save the latest confirmed 30m trend.
    """

    state["gold-30m-trend"] = {
        "trend": trend,
        "timestamp": timestamp
    }