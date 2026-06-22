from __future__ import annotations

from pathlib import Path

from app.actions import Action


class ResumePromptMode:
    def __init__(self, app, path: Path, resume_item: dict, return_mode) -> None:
        self.app = app
        self.path = path
        self.resume_item = resume_item
        self.return_mode = return_mode
        self.items = ["RESUME", "START OVER", "CANCEL"]
        self.selected = 0

    def handle_action(self, action: Action) -> None:
        if action == Action.UP:
            self.selected = (self.selected - 1) % len(self.items)
        elif action == Action.DOWN:
            self.selected = (self.selected + 1) % len(self.items)
        elif action in (Action.BACK, Action.HOME):
            self.app.set_mode(self.return_mode)
        elif action == Action.QUIT:
            self.app.quit()
        elif action == Action.SELECT:
            if self.selected == 0:
                self.app.play_video_now(self.path, start_seconds=self.resume_item.get("position_seconds"), return_mode=self.return_mode)
            elif self.selected == 1:
                self.app.resume_state.clear(self.path)
                self.app.play_video_now(self.path, start_seconds=None, return_mode=self.return_mode)
            else:
                self.app.set_mode(self.return_mode)

    def draw(self, ui) -> None:
        ui.clear()
        ui.text("RESUME PLAYBACK?", ui.margin_x, ui.margin_y, "large")
        ui.text(str(self.resume_item.get("display_name") or self.path.stem), ui.margin_x, ui.margin_y + 86, "small")
        ui.text(self._progress_text(), ui.margin_x, ui.margin_y + 122, "small")
        ui.menu(
            "",
            self.items,
            self.selected,
            footer="ENTER: SELECT   BACK: CANCEL",
            start_y=ui.margin_y + 178,
            clear_screen=False,
        )

    def _progress_text(self) -> str:
        position = _format_seconds(self.resume_item.get("position_seconds"))
        duration = _format_seconds(self.resume_item.get("duration_seconds"))
        if duration:
            return f"{position} / {duration}"
        return position


def _format_seconds(value) -> str:
    try:
        total = int(float(value))
    except (TypeError, ValueError):
        return "0:00"
    total = max(0, total)
    hours = total // 3600
    minutes = (total % 3600) // 60
    seconds = total % 60
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"
