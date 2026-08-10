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
        json.dump(state, file, indent=4)