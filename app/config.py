import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT_DIR / "config.json"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"config.json not found: {CONFIG_FILE}"
        )

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    if "rules" not in config:
        raise ValueError("config.json must contain 'rules'.")

    if not isinstance(config["rules"], list):
        raise ValueError("'rules' must be a list.")

    required_fields = [
        "id",
        "name",
        "enabled",
        "exchange",
        "symbol",
        "timeframe",
        "ema",
        "direction"
    ]

    for rule in config["rules"]:
        for field in required_fields:
            if field not in rule:
                raise ValueError(
                    f"Missing '{field}' in rule '{rule.get('id', 'unknown')}'."
                )

        if rule["direction"] not in ["above", "below", "both"]:
            raise ValueError(
                f"Invalid direction '{rule['direction']}' in rule '{rule['id']}'."
            )

    config.setdefault("debug", False)

    return config