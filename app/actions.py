from enum import Enum, auto


class Action(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    SELECT = auto()
    BACK = auto()
    HOME = auto()
    PLAY_PAUSE = auto()
    STOP = auto()
    SEEK_FORWARD = auto()
    SEEK_BACK = auto()
    RANDOM = auto()
    LEFT_DIAL_CW = auto()
    LEFT_DIAL_CCW = auto()
    LEFT_DIAL_PRESS = auto()
    RIGHT_DIAL_CW = auto()
    RIGHT_DIAL_CCW = auto()
    RIGHT_DIAL_PRESS = auto()
    QUIT = auto()
