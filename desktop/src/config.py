import json
from pathlib import Path
from typing import Any

DESKTOP_DIR = Path(__file__).resolve().parent.parent
SETTINGS_PATH = DESKTOP_DIR / "settings.json"
DEFAULT_SETTINGS = {
    "api_base_url": "http://localhost:8000",
    "connection_timeout_seconds": 30,
}


def load_settings() -> dict[str, Any]:
    if not SETTINGS_PATH.exists():
        return DEFAULT_SETTINGS.copy()

    try:
        with SETTINGS_PATH.open(encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return DEFAULT_SETTINGS.copy()

    settings = DEFAULT_SETTINGS.copy()
    settings.update({k: v for k, v in data.items() if k in DEFAULT_SETTINGS})
    return settings


def save_settings(settings: dict[str, Any]) -> None:
    merged = DEFAULT_SETTINGS.copy()
    merged.update({k: v for k, v in settings.items() if k in DEFAULT_SETTINGS})
    with SETTINGS_PATH.open("w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")
