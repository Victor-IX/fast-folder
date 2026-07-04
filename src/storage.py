from __future__ import annotations

import json
from pathlib import Path

CONFIG_DIR_NAME = ".ff"
LOCATIONS_FILE_NAME = "locations.json"


def get_config_dir() -> Path:
    config_dir = Path.home() / CONFIG_DIR_NAME
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_locations_file() -> Path:
    return get_config_dir() / LOCATIONS_FILE_NAME


def load_locations() -> dict[str, str]:
    locations_file = get_locations_file()
    if not locations_file.exists():
        return {}
    try:
        data = json.loads(locations_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(name): str(path) for name, path in data.items()}


def save_locations(locations: dict[str, str]) -> None:
    locations_file = get_locations_file()
    locations_file.write_text(json.dumps(locations, indent=2, sort_keys=True), encoding="utf-8")
