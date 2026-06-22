from __future__ import annotations

from typing import Iterable

import pygame

from app.config import resolve_path


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
        self.medium = self._load_crt_font(int(ui_config["font_size_medium"]))
        self.small = self._load_crt_font(int(ui_config["font_size_small"]))
        self.show_text_title_if_logo_missing = bool(ui_config.get("show_text_title_if_logo_missing", True))
        self.logo = self._load_logo(ui_config.get("logo_path"))

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
        show_logo: bool = False,
        clear_screen: bool = True,
    ) -> None:
        if clear_screen:
            self.clear()
        title_height = self._draw_title(title, show_logo)

        title_gap = 58 if show_logo and self.logo is not None else 40
        y = start_y if start_y is not None else max(self.margin_y + 104, self.margin_y + title_height + title_gap)
        cursor_x = self.margin_x
        text_x = self.margin_x + 32
        cursor_visible = (pygame.time.get_ticks() // 500) % 2 == 0
        for index, item in enumerate(items):
            item_height = self.text(item, text_x, y, "medium")
            if index == selected_index and cursor_visible:
                cursor_rect = pygame.Rect(cursor_x, y + 8, 16, max(16, item_height - 16))
                pygame.draw.rect(self.screen, self.text_color, cursor_rect)
            y += max(46, item_height + 12)

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

    def _load_crt_font(self, size: int) -> pygame.font.Font:
        candidates = [
            "menlo",
            "monaco",
            "dejavusansmono",
            "liberationmono",
            "couriernew",
            "courier",
        ]
        for name in candidates:
            font_path = pygame.font.match_font(name, bold=True)
            if font_path:
                return pygame.font.Font(font_path, size)
        return pygame.font.Font(None, size)

    def _draw_title(self, title: str, show_logo: bool) -> int:
        if show_logo and self.logo is not None:
            self.screen.blit(self.logo, (self.margin_x, self.margin_y))
            return self.logo.get_height()

        if not show_logo or self.show_text_title_if_logo_missing:
            return self.text(title, self.margin_x, self.margin_y, "large")

        return 0

    def _load_logo(self, logo_path: str | None) -> pygame.Surface | None:
        if not logo_path:
            return None

        path = resolve_path(logo_path)
        if not path.exists() or not path.is_file():
            return None

        try:
            image = pygame.image.load(str(path)).convert_alpha()
        except pygame.error:
            return None

        max_width = self.screen.get_width() - (self.margin_x * 2)
        max_height = 64
        width, height = image.get_size()
        if width <= 0 or height <= 0:
            return None

        scale = min(max_width / width, max_height / height, 1.0)
        if scale < 1.0:
            size = (max(1, int(width * scale)), max(1, int(height * scale)))
            image = pygame.transform.smoothscale(image, size)

        return image
