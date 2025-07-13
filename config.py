import json
from pathlib import Path

CONFIG_PATH = Path("data/config.json")
STATS_PATH = Path("data/stats.json")

DEFAULT_CONFIG = {
    "enabled": True,
    "dumping": False,
    "adaptive": True,
    "proposal": {"tons": 50, "price": 7803},
    "target": {"location": "-", "min_volume": 20, "max_volume": 60, "min_price": 7500},
    "whitelist": [123456789]
}

DEFAULT_STATS = {
    "taken_with_dump": 0,
    "taken_without_dump": 0,
    "rejected": 0,
    "filtered_out": 0,
    "cache": []  # кэш номеров обработанных заказов
}

def load_json(path: Path, default: dict) -> dict:
    if not path.exists():
        save_json(path, default)
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: Path, data: dict):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_config() -> dict:
    return load_json(CONFIG_PATH, DEFAULT_CONFIG)

def save_config(data: dict):
    save_json(CONFIG_PATH, data)

def get_stats() -> dict:
    return load_json(STATS_PATH, DEFAULT_STATS)

def save_stats(data: dict):
    save_json(STATS_PATH, data)