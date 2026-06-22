from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import library_path, resolve_path, simpsons_path
from app.media_library import display_name


class ResumeState:
    def __init__(self, config: dict) -> None:
        resume_config = config.get("resume", {})
        self.enabled = bool(resume_config.get("enabled", True))
        self.state_file = resolve_path(resume_config.get("state_file", "./data/playback_state.json"))
        self.minimum_position = float(resume_config.get("minimum_position_seconds", 60))
        self.completion_threshold = float(resume_config.get("completion_threshold_percent", 92))
        self.simpsons_root = simpsons_path(config)
        self.library_root = library_path(config)

    def get(self, path: Path) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        item_id = self.item_id(path)
        data = self._load()
        item = data.get("items", {}).get(item_id)
        if not isinstance(item, dict):
            return None
        if item.get("completed"):
            return None
        position = _number_or_none(item.get("position_seconds"))
        if position is None or position < self.minimum_position:
            return None
        return item

    def clear(self, path: Path) -> None:
        if not self.enabled:
            return
        item_id = self.item_id(path)
        data = self._load()
        items = data.setdefault("items", {})
        if item_id in items:
            del items[item_id]
            self._save(data)

    def save_playback(self, path: Path, position, duration) -> None:
        if not self.enabled:
            return

        position_seconds = _number_or_none(position)
        duration_seconds = _number_or_none(duration)
        if position_seconds is None:
            return

        position_seconds = max(0.0, position_seconds)
        if duration_seconds is not None:
            duration_seconds = max(0.0, duration_seconds)
            if duration_seconds <= 0:
                duration_seconds = None

        item_id = self.item_id(path)
        data = self._load()
        items = data.setdefault("items", {})

        percent = None
        if duration_seconds:
            percent = min(100.0, max(0.0, (position_seconds / duration_seconds) * 100))

        if position_seconds < self.minimum_position or (percent is not None and percent >= self.completion_threshold):
            items.pop(item_id, None)
            self._save(data)
            return

        items[item_id] = {
            "display_name": display_name(path),
            "absolute_path": str(path.resolve()),
            "position_seconds": round(position_seconds, 2),
            "duration_seconds": round(duration_seconds, 2) if duration_seconds is not None else None,
            "percent": round(percent, 2) if percent is not None else None,
            "updated_at": datetime.now().isoformat(timespec="seconds"),
            "completed": False,
        }
        self._save(data)

    def item_id(self, path: Path) -> str:
        resolved = path.resolve()
        for prefix, root in (("library", self.library_root), ("simpsons", self.simpsons_root)):
            try:
                relative = resolved.relative_to(root.resolve())
            except ValueError:
                continue
            return f"{prefix}/{relative.as_posix()}"
        return resolved.name

    def _load(self) -> dict[str, Any]:
        if not self.state_file.exists():
            return {"items": {}}
        try:
            with self.state_file.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return {"items": {}}
        if not isinstance(data, dict) or not isinstance(data.get("items"), dict):
            return {"items": {}}
        return data

    def _save(self, data: dict[str, Any]) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with self.state_file.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")


def _number_or_none(value) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number:
        return None
    return number
