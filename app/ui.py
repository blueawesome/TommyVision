from __future__ import annotations

from typing import Iterable

import pygame


COLORS = {
    "blue": (0, 36, 156),
    "white": (255, 255, 255),
}


class UI:
    def __init__(self, screen: pygame.Surface, config: dict) -> None:
        self.screen = screen
        ui_config = config["ui"]
        self.background = COLORS.get(ui_config["background_color"], COLORS["blue"])
        self.text_color = COLORS.get(ui_config["text_color"], COLORS["white"])
        self.margin_x = int(ui_config["safe_margin_x"])
        self.margin_y = int(ui_config["safe_margin_y"])
        self.large = pygame.font.Font(None, int(ui_config["font_size_large"]))
        self.medium = pygame.font.Font(None, int(ui_config["font_size_medium"]))
        self.small = pygame.font.Font(None, int(ui_config["font_size_small"]))

    def clear(self) -> None:
        self.screen.fill(self.background)

    def text(
        self,
        value: str,
        x: int,
        y: int,
        size: str = "medium",
        color: tuple[int, int, int] | None = None,
    ) -> int:
        font = self._font(size)
        surface = font.render(value, True, color or self.text_color)
        self.screen.blit(surface, (x, y))
        return surface.get_height()

    def centered_text(self, value: str, y: int, size: str = "medium") -> int:
        font = self._font(size)
        surface = font.render(value, True, self.text_color)
        x = (self.screen.get_width() - surface.get_width()) // 2
        self.screen.blit(surface, (x, y))
        return surface.get_height()

    def menu(
        self,
        title: str,
        items: Iterable[str],
        selected_index: int,
        footer: str = "",
        start_y: int | None = None,
    ) -> None:
        self.clear()
        self.text(title, self.margin_x, self.margin_y, "large")

        y = start_y if start_y is not None else self.margin_y + 88
        for index, item in enumerate(items):
            prefix = "> " if index == selected_index else "  "
            self.text(prefix + item, self.margin_x, y, "medium")
            y += 38

        if footer:
            self.text(footer, self.margin_x, self.screen.get_height() - self.margin_y - 26, "small")

    def message(self, title: str, lines: list[str], footer: str = "BACK: MENU") -> None:
        self.clear()
        self.text(title, self.margin_x, self.margin_y, "large")
        y = self.margin_y + 92
        for line in lines:
            self.text(line, self.margin_x, y, "medium")
            y += 36
        if footer:
            self.text(footer, self.margin_x, self.screen.get_height() - self.margin_y - 26, "small")

    def _font(self, size: str) -> pygame.font.Font:
        if size == "large":
            return self.large
        if size == "small":
            return self.small
        return self.medium
