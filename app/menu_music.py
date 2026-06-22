from __future__ import annotations

import random
from pathlib import Path

import pygame

from app.config import resolve_path


AUDIO_EXTENSIONS = {".mp3", ".ogg", ".wav"}


class MenuMusic:
    def __init__(self, config: dict) -> None:
        audio_config = config.get("audio", {})
        self.enabled = bool(audio_config.get("menu_music_enabled", False))
        self.folder = resolve_path(audio_config.get("menu_music_folder", "./assets/menu_music"))
        self.volume = _clamp_volume(audio_config.get("menu_music_volume", 0.35))
        self.shuffle = bool(audio_config.get("shuffle", True))
        self.tracks: list[Path] = []
        self.index = 0
        self.ready = False

        if self.enabled:
            self._setup()

    def start(self) -> None:
        if not self.ready or not self.tracks:
            return
        if pygame.mixer.music.get_busy():
            return
        self._play_next()

    def update(self) -> None:
        if not self.ready or not self.tracks:
            return
        if not pygame.mixer.music.get_busy():
            self._play_next()

    def stop(self) -> None:
        if not self.ready:
            return
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            self.ready = False

    def shutdown(self) -> None:
        self.stop()

    def _setup(self) -> None:
        if not self.folder.exists() or not self.folder.is_dir():
            return

        self.tracks = [
            path
            for path in self.folder.iterdir()
            if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS and _looks_like_audio(path)
        ]
        if not self.tracks:
            return

        self.tracks.sort(key=lambda path: path.name.lower())
        if self.shuffle:
            random.shuffle(self.tracks)

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.set_volume(self.volume)
        except pygame.error:
            return

        self.ready = True

    def _play_next(self) -> None:
        attempts = len(self.tracks)
        while attempts:
            track = self.tracks[self.index]
            self.index = (self.index + 1) % len(self.tracks)
            if self.shuffle and self.index == 0:
                random.shuffle(self.tracks)

            try:
                pygame.mixer.music.load(str(track))
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play()
                return
            except pygame.error:
                attempts -= 1

        self.ready = False


def _clamp_volume(value) -> float:
    try:
        volume = float(value)
    except (TypeError, ValueError):
        volume = 0.35
    return max(0.0, min(1.0, volume))


def _looks_like_audio(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            header = handle.read(12)
    except OSError:
        return False

    suffix = path.suffix.lower()
    if suffix == ".wav":
        return header.startswith(b"RIFF") and header[8:12] == b"WAVE"
    if suffix == ".ogg":
        return header.startswith(b"OggS")
    if suffix == ".mp3":
        return header.startswith(b"ID3") or (
            len(header) >= 2 and header[0] == 0xFF and (header[1] & 0xE0) == 0xE0
        )
    return False
