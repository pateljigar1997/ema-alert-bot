import json
from pathlib import Path

CONFIG_FILE = Path("config.json")


def load_config():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"{CONFIG_FILE} not found.")

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        config = json.load(file)

    required_fields = [
        "id",
        "name",
        "enabled",
        "exchange",
        "symbol",
        "timeframe",
        "ema",
        "direction",
    ]

    for rule in config["rules"]:
        for field in required_fields:
            if field not in rule:
                raise ValueError(
                    f"Missing '{field}' in rule '{rule.get('id', 'unknown')}'."
                )

    return config