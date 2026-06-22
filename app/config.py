from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:
    yaml = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "library.yaml"


DEFAULT_CONFIG: dict[str, Any] = {
    "app": {
        "title": "TOMMYVISION",
        "fullscreen": False,
        "width": 640,
        "height": 480,
    },
    "paths": {
        "simpsons": "./sample_media/simpsons",
        "library": "./sample_media/library",
    },
    "player": {
        "command": "mpv",
        "fullscreen": True,
        "extra_args": ["--fs", "--really-quiet"],
    },
    "ui": {
        "background_color": "blue",
        "text_color": "white",
        "safe_margin_x": 48,
        "safe_margin_y": 36,
        "font_size_large": 48,
        "font_size_medium": 32,
        "font_size_small": 24,
    },
}


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    config_path = Path(path)
    data: dict[str, Any] = {}

    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as handle:
            if yaml is not None:
                loaded = yaml.safe_load(handle) or {}
            else:
                loaded = _load_simple_yaml(handle.read())
            if isinstance(loaded, dict):
                data = loaded

    return _merge(DEFAULT_CONFIG, data)


def resolve_path(path_value: str | Path) -> Path:
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_simple_yaml(text: str) -> dict[str, Any]:
    config: dict[str, Any] = {}
    section: str | None = None
    list_key: str | None = None

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 0 and line.endswith(":"):
            section = line[:-1]
            config[section] = {}
            list_key = None
            continue

        if section is None:
            continue

        if line.startswith("- ") and list_key:
            config[section][list_key].append(_coerce_value(line[2:]))
            continue

        if ":" not in line:
            continue

        key, value = [part.strip() for part in line.split(":", 1)]
        if value == "":
            config[section][key] = []
            list_key = key
        else:
            config[section][key] = _coerce_value(value)
            list_key = None

    return config


def _coerce_value(value: str) -> Any:
    value = value.strip().strip('"').strip("'")
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        return int(value)
    except ValueError:
        return value
