from __future__ import annotations

import subprocess
from pathlib import Path


class PlaybackError(Exception):
    pass


class Player:
    def __init__(self, config: dict) -> None:
        player_config = config["player"]
        self.command = str(player_config.get("command", "mpv"))
        self.extra_args = list(player_config.get("extra_args", []))

    def play(self, path: Path) -> None:
        command = [self.command, *self.extra_args, str(path)]
        self._run(command)

    def play_optional(self, path: Path) -> bool:
        try:
            self._run([self.command, *self.extra_args, str(path)])
        except PlaybackError:
            return False
        return True

    def _run(self, command: list[str]) -> None:
        try:
            subprocess.run(command, check=False)
        except FileNotFoundError as exc:
            raise PlaybackError(f"Could not find player command: {self.command}") from exc
        except OSError as exc:
            raise PlaybackError(f"Could not start playback: {exc}") from exc
