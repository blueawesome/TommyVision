from __future__ import annotations

import pygame

from app.config import load_config, resolve_path
from app.input_keyboard import action_from_event
from app.modes.crt_library import CRTLibraryMode
from app.modes.error_screen import ErrorScreenMode
from app.modes.main_menu import MainMenuMode
from app.modes.retro_games import RetroGamesMode
from app.modes.simpsons import SimpsonsMode
from app.player import PlaybackError, Player
from app.ui import UI


class TommyVisionApp:
    def __init__(self) -> None:
        self.config = load_config()
        app_config = self.config["app"]
        self.title = str(app_config["title"])
        self.running = True

        pygame.init()
        flags = pygame.FULLSCREEN if app_config.get("fullscreen") else 0
        size = (int(app_config["width"]), int(app_config["height"]))
        self.screen = pygame.display.set_mode(size, flags)
        pygame.display.set_caption(self.title)
        self.clock = pygame.time.Clock()
        self.ui = UI(self.screen, self.config)
        self.player = Player(self.config)
        self.mode = MainMenuMode(self)

    def run(self) -> None:
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    continue
                action = action_from_event(event)
                if action is not None:
                    self.mode.handle_action(action)

            self.mode.draw(self.ui)
            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()

    def set_mode(self, mode) -> None:
        self.mode = mode

    def go_home(self) -> None:
        self.mode = MainMenuMode(self)

    def open_simpsons(self) -> None:
        self.mode = SimpsonsMode(self, resolve_path(self.config["paths"]["simpsons"]))

    def open_crt_library(self) -> None:
        self.mode = CRTLibraryMode(self, resolve_path(self.config["paths"]["library"]))

    def open_retro_games(self) -> None:
        self.mode = RetroGamesMode(self)

    def play_video(self, path) -> None:
        return_mode = self.mode
        try:
            pygame.display.iconify()
            self.player.play(path)
        except PlaybackError as exc:
            self.mode = ErrorScreenMode(self, "PLAYBACK ERROR", str(exc), return_mode)
        finally:
            pygame.event.clear()
            if self.mode is return_mode:
                self.mode = return_mode

    def quit(self) -> None:
        self.running = False


def main() -> None:
    TommyVisionApp().run()


if __name__ == "__main__":
    main()
