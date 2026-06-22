from __future__ import annotations

from app.actions import Action


class ErrorScreenMode:
    def __init__(self, app, title: str, message: str, return_mode) -> None:
        self.app = app
        self.title = title
        self.message = message
        self.return_mode = return_mode

    def handle_action(self, action: Action) -> None:
        if action in (Action.BACK, Action.SELECT, Action.LEFT_DIAL_PRESS):
            self.app.set_mode(self.return_mode)
        elif action == Action.HOME:
            self.app.go_home()
        elif action == Action.QUIT:
            self.app.quit()

    def draw(self, ui) -> None:
        ui.message(self.title, self._wrapped_lines(), footer="BACK: RETURN   H: MENU")

    def _wrapped_lines(self) -> list[str]:
        words = self.message.split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if len(candidate) > 34 and current:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        return lines or [self.message]
