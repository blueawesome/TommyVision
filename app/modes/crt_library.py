from __future__ import annotations

from pathlib import Path

from app.actions import Action
from app.media_library import display_name, is_video_file, list_library_items, random_video


class CRTLibraryMode:
    PAGE_SIZE = 8

    def __init__(self, app, root: Path) -> None:
        self.app = app
        self.root = root
        self.current_folder = root
        self.selected = 0

    def handle_action(self, action: Action) -> None:
        items = self._items()
        if action == Action.HOME:
            self.app.go_home()
        elif action == Action.QUIT:
            self.app.quit()
        elif action == Action.BACK:
            self._go_back()
        elif action == Action.UP and items:
            self.selected = (self.selected - 1) % len(items)
        elif action == Action.DOWN and items:
            self.selected = (self.selected + 1) % len(items)
        elif action == Action.RANDOM:
            video = random_video(self.current_folder)
            if video:
                self.app.play_video(video)
        elif action == Action.SELECT and items:
            self._open(items[self.selected])

    def draw(self, ui) -> None:
        if not self.root.exists() or not self.root.is_dir():
            ui.message("CRT LIBRARY", ["Library folder missing.", f"Check: {self.root}"], footer="BACK: MENU")
            return

        items = self._items()
        title = "CRT LIBRARY"
        if self.current_folder != self.root:
            title = self.current_folder.name.upper()

        if not items:
            ui.message(title, ["No folders or videos found."], footer="BACK: UP   H: MENU")
            return

        start = (self.selected // self.PAGE_SIZE) * self.PAGE_SIZE
        visible = items[start:start + self.PAGE_SIZE]
        labels = [self._label(path) for path in visible]
        ui.menu(
            title,
            labels,
            self.selected - start,
            footer="ENTER: OPEN/PLAY   BACK: UP   H: MENU",
            start_y=112,
        )

    def _items(self) -> list[Path]:
        return list_library_items(self.current_folder)

    def _open(self, path: Path) -> None:
        if path.is_dir():
            self.current_folder = path
            self.selected = 0
        elif is_video_file(path):
            self.app.play_video(path)

    def _go_back(self) -> None:
        if self.current_folder == self.root:
            self.app.go_home()
            return
        self.current_folder = self.current_folder.parent
        self.selected = 0

    def _label(self, path: Path) -> str:
        prefix = "[DIR] " if path.is_dir() else ""
        return prefix + display_name(path)
