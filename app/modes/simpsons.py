from __future__ import annotations

import random

from app.actions import Action
from app.media_library import scan_simpsons


class SimpsonsMode:
    def __init__(self, app, root) -> None:
        self.app = app
        self.root = root
        self.seasons = scan_simpsons(root)
        self.season_index = 0
        self.episode_index = 0

    def handle_action(self, action: Action) -> None:
        if action in (Action.BACK, Action.HOME, Action.LEFT_DIAL_PRESS):
            self.app.go_home()
        elif action == Action.QUIT:
            self.app.quit()
        elif not self.seasons:
            return
        elif action in (Action.LEFT, Action.LEFT_DIAL_CCW):
            self._change_season(-1)
        elif action in (Action.RIGHT, Action.LEFT_DIAL_CW):
            self._change_season(1)
        elif action in (Action.UP, Action.RIGHT_DIAL_CCW):
            self._change_episode(-1)
        elif action in (Action.DOWN, Action.RIGHT_DIAL_CW):
            self._change_episode(1)
        elif action == Action.RANDOM:
            self._random_episode()
        elif action in (Action.SELECT, Action.RIGHT_DIAL_PRESS):
            self.app.play_video(self.current_episode().path)

    def draw(self, ui) -> None:
        if not self.seasons:
            ui.message(
                "THE SIMPSONS",
                [
                    "No episodes found.",
                    f"Check: {self.root}",
                ],
                footer="BACK: MENU",
            )
            return

        season = self.current_season()
        episode = self.current_episode()
        ui.clear()
        ui.text("THE SIMPSONS", ui.margin_x, ui.margin_y, "large")
        ui.text(f"SEASON {season.number:02d}", ui.margin_x, ui.margin_y + 106, "medium")
        ui.text(f"EPISODE {episode.number:02d}", ui.margin_x, ui.margin_y + 146, "medium")
        ui.text(episode.label, ui.margin_x, ui.margin_y + 202, "small")
        ui.text("A/D SEASON   J/L EPISODE", ui.margin_x, 378, "small")
        ui.text("ENTER/K: PLAY   BACK/S: MENU", ui.margin_x, 410, "small")

    def current_season(self):
        return self.seasons[self.season_index]

    def current_episode(self):
        season = self.current_season()
        self.episode_index = min(self.episode_index, len(season.episodes) - 1)
        return season.episodes[self.episode_index]

    def _change_season(self, direction: int) -> None:
        self.season_index = (self.season_index + direction) % len(self.seasons)
        self.episode_index = min(self.episode_index, len(self.current_season().episodes) - 1)

    def _change_episode(self, direction: int) -> None:
        episodes = self.current_season().episodes
        self.episode_index = (self.episode_index + direction) % len(episodes)

    def _random_episode(self) -> None:
        self.season_index = random.randrange(len(self.seasons))
        episodes = self.current_season().episodes
        self.episode_index = random.randrange(len(episodes))
