from __future__ import annotations

from app.actions import Action


class RetroGamesMode:
    def __init__(self, app) -> None:
        self.app = app

    def handle_action(self, action: Action) -> None:
        if action in (Action.BACK, Action.HOME, Action.LEFT_DIAL_PRESS):
            self.app.go_home()
        elif action == Action.QUIT:
            self.app.quit()

    def draw(self, ui) -> None:
        ui.message(
            "RETRO GAMES",
            [
                "This mode will eventually",
                "launch RetroPie or",
                "EmulationStation.",
            ],
            footer="BACK: MENU",
        )
