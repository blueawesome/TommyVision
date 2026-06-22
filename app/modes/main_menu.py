from __future__ import annotations

from app.actions import Action


class MainMenuMode:
    def __init__(self, app) -> None:
        self.app = app
        self.items = ["THE SIMPSONS", "CRT LIBRARY", "RETRO GAMES"]
        self.selected = 0

    def handle_action(self, action: Action) -> None:
        if action == Action.UP:
            self.selected = (self.selected - 1) % len(self.items)
        elif action == Action.DOWN:
            self.selected = (self.selected + 1) % len(self.items)
        elif action == Action.SELECT:
            if self.selected == 0:
                self.app.open_simpsons()
            elif self.selected == 1:
                self.app.open_crt_library()
            else:
                self.app.open_retro_games()
        elif action in (Action.BACK, Action.QUIT):
            self.app.quit()

    def draw(self, ui) -> None:
        ui.menu(self.app.title, self.items, self.selected, footer="ENTER: SELECT   Q/ESC: QUIT", show_logo=True)
