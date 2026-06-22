from __future__ import annotations

import random
import re
from dataclasses import dataclass
from pathlib import Path


VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".m4v", ".mpg", ".mpeg"}
SEASON_RE = re.compile(r"season\s*(\d+)|s(\d+)", re.IGNORECASE)
EPISODE_RE = re.compile(r"s(\d{1,2})\s*e(\d{1,2})", re.IGNORECASE)


@dataclass(frozen=True)
class Episode:
    label: str
    path: Path
    number: int


@dataclass(frozen=True)
class Season:
    label: str
    path: Path
    number: int
    episodes: list[Episode]


def is_video_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS


def display_name(path: Path) -> str:
    if is_video_file(path):
        return path.stem
    return path.name


def scan_simpsons(root: Path) -> list[Season]:
    if not root.exists() or not root.is_dir():
        return []

    seasons: list[Season] = []
    for season_dir in sorted([path for path in root.iterdir() if path.is_dir()], key=_season_sort_key):
        episodes = _scan_episodes(season_dir)
        if episodes:
            seasons.append(
                Season(
                    label=season_dir.name,
                    path=season_dir,
                    number=_season_number(season_dir),
                    episodes=episodes,
                )
            )
    return seasons


def list_library_items(folder: Path) -> list[Path]:
    if not folder.exists() or not folder.is_dir():
        return []

    items = [
        path
        for path in folder.iterdir()
        if path.is_dir() or is_video_file(path)
    ]
    return sorted(items, key=lambda path: (not path.is_dir(), path.name.lower()))


def random_video(folder: Path) -> Path | None:
    if not folder.exists() or not folder.is_dir():
        return None
    files = [path for path in folder.rglob("*") if is_video_file(path)]
    if not files:
        return None
    return random.choice(files)


def _scan_episodes(season_dir: Path) -> list[Episode]:
    files = [path for path in season_dir.iterdir() if is_video_file(path)]
    sorted_files = sorted(files, key=_episode_sort_key)
    episodes: list[Episode] = []
    for index, path in enumerate(sorted_files, start=1):
        episodes.append(Episode(label=display_name(path), path=path, number=_episode_number(path, index)))
    return episodes


def _season_sort_key(path: Path) -> tuple[int, str]:
    return (_season_number(path), path.name.lower())


def _season_number(path: Path) -> int:
    match = SEASON_RE.search(path.name)
    if not match:
        return 999
    value = match.group(1) or match.group(2)
    return int(value)


def _episode_sort_key(path: Path) -> tuple[int, str]:
    match = EPISODE_RE.search(path.name)
    if match:
        return (int(match.group(2)), path.name.lower())
    return (999, path.name.lower())


def _episode_number(path: Path, fallback: int) -> int:
    match = EPISODE_RE.search(path.name)
    if not match:
        return fallback
    return int(match.group(2))
