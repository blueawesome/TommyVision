from __future__ import annotations

import time

import pygame

from app.actions import Action
from app.config import library_path, load_config, resolve_path, simpsons_path
from app.input_keyboard import action_from_event
from app.menu_music import MenuMusic
from app.modes.crt_library import CRTLibraryMode
from app.modes.error_screen import ErrorScreenMode
from app.modes.main_menu import MainMenuMode
from app.modes.retro_games import RetroGamesMode
from app.modes.resume_prompt import ResumePromptMode
from app.modes.simpsons import SimpsonsMode
from app.playback_session import STOP_EXIT_CODE, PlaybackSession
from app.player import PlaybackError, Player
from app.resume_state import ResumeState
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
        self._play_boot_video_if_enabled()
        self.menu_music = MenuMusic(self.config)
        self.resume_state = ResumeState(self.config)
        self.mode = MainMenuMode(self)
        self.menu_music.start()

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
            self.menu_music.update()
            pygame.display.flip()
            self.clock.tick(30)

        self.menu_music.shutdown()
        pygame.quit()

    def set_mode(self, mode) -> None:
        self.mode = mode

    def go_home(self) -> None:
        self.mode = MainMenuMode(self)

    def open_simpsons(self) -> None:
        self.mode = SimpsonsMode(self, simpsons_path(self.config))

    def open_crt_library(self) -> None:
        self.mode = CRTLibraryMode(self, library_path(self.config))

    def open_retro_games(self) -> None:
        self.mode = RetroGamesMode(self)

    def play_video(self, path) -> None:
        return_mode = self.mode
        resume_item = self.resume_state.get(path)
        if resume_item is not None:
            self.mode = ResumePromptMode(self, path, resume_item, return_mode)
            return
        self.play_video_now(path, return_mode=return_mode)

    def play_video_now(self, path, start_seconds=None, return_mode=None) -> None:
        if return_mode is None:
            return_mode = self.mode
        session = PlaybackSession(self.config, path, start_seconds=start_seconds)
        try:
            self.menu_music.stop()
            pygame.display.iconify()
            session.start()
            self._run_playback_session(session)
        except PlaybackError as exc:
            self.mode = ErrorScreenMode(self, "PLAYBACK ERROR", str(exc), return_mode)
        finally:
            session.cleanup()
            self.menu_music.start()
            pygame.event.clear()
            if not isinstance(self.mode, ErrorScreenMode):
                self.mode = return_mode

    def quit(self) -> None:
        self.running = False

    def _play_boot_video_if_enabled(self) -> None:
        startup_config = self.config.get("startup", {})
        if not startup_config.get("play_boot_video", False):
            return

        boot_video = resolve_path(startup_config.get("boot_video", ""))
        if not boot_video.exists() or not boot_video.is_file():
            return

        pygame.display.iconify()
        self.player.play_optional(boot_video)
        pygame.event.clear()

    def _run_playback_session(self, session: PlaybackSession) -> None:
        last_poll = 0.0
        while session.is_running() and self.running:
            now = time.monotonic()
            if now - last_poll >= 5.0:
                session.refresh_position()
                last_poll = now

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    session.stop_and_save(self.resume_state)
                    self.quit()
                    break

                action = action_from_event(event)
                if action == Action.STOP:
                    session.stop_and_save(self.resume_state)
                elif action == Action.PLAY_PAUSE:
                    session.play_pause()
                elif action == Action.RIGHT:
                    session.seek(10)
                elif action == Action.LEFT:
                    session.seek(-10)

            self.clock.tick(20)

        session.wait()
        if session.returncode() == STOP_EXIT_CODE:
            session.save_latest(self.resume_state)


def main() -> None:
    TommyVisionApp().run()


if __name__ == "__main__":
    main()
