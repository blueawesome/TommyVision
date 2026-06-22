from __future__ import annotations

import pygame

from app.actions import Action


KEY_ACTIONS = {
    pygame.K_UP: Action.UP,
    pygame.K_DOWN: Action.DOWN,
    pygame.K_LEFT: Action.LEFT,
    pygame.K_RIGHT: Action.RIGHT,
    pygame.K_RETURN: Action.SELECT,
    pygame.K_KP_ENTER: Action.SELECT,
    pygame.K_BACKSPACE: Action.BACK,
    pygame.K_ESCAPE: Action.BACK,
    pygame.K_h: Action.HOME,
    pygame.K_r: Action.RANDOM,
    pygame.K_q: Action.QUIT,
    pygame.K_x: Action.STOP,
    pygame.K_SPACE: Action.PLAY_PAUSE,
    pygame.K_a: Action.LEFT_DIAL_CCW,
    pygame.K_d: Action.LEFT_DIAL_CW,
    pygame.K_s: Action.LEFT_DIAL_PRESS,
    pygame.K_j: Action.RIGHT_DIAL_CCW,
    pygame.K_l: Action.RIGHT_DIAL_CW,
    pygame.K_k: Action.RIGHT_DIAL_PRESS,
}


def action_from_event(event: pygame.event.Event) -> Action | None:
    if event.type != pygame.KEYDOWN:
        return None
    return KEY_ACTIONS.get(event.key)
