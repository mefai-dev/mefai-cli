"""Configuration management for MEFAI CLI.

Reads and writes ~/.mefai/config.yaml for persistent settings
like base_url and api_key.
"""

from pathlib import Path
from typing import Any

import yaml


CONFIG_DIR = Path.home() / ".mefai"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG: dict[str, Any] = {
    "base_url": "http://localhost:8080",
    "api_key": "",
    "default_timeframe": "1h",
    "default_limit": 100,
    "ws_url": "ws://localhost:8080/ws",
}


def ensure_config_dir() -> None:
    """Create the config directory if it does not exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict[str, Any]:
    """Load config from disk. Returns defaults if file is missing."""
    if not CONFIG_FILE.exists():
        return dict(DEFAULT_CONFIG)
    with open(CONFIG_FILE, "r") as f:
        data = yaml.safe_load(f) or {}
    merged = dict(DEFAULT_CONFIG)
    merged.update(data)
    return merged


def save_config(config: dict[str, Any]) -> None:
    """Persist config to ~/.mefai/config.yaml."""
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False)


def get_base_url() -> str:
    """Return the configured base URL for the MEFAI Engine API."""
    return str(load_config().get("base_url", DEFAULT_CONFIG["base_url"]))


def get_api_key() -> str:
    """Return the configured API key."""
    return str(load_config().get("api_key", ""))


def get_ws_url() -> str:
    """Return the configured WebSocket URL."""
    return str(load_config().get("ws_url", DEFAULT_CONFIG["ws_url"]))
