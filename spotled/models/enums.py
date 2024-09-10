from enum import Enum

class ScreenMode(Enum):
    NORMAL = 0
    UPSIDE_DOWN = 1
    MIRROR = 2
    MIRROR_UPSIDE_DOWN = 3

class Effect(Enum):
    NONE = 0
    SCROLL_UP = 1
    SCROLL_DOWN = 2
    SCROLL_LEFT = 3
    SCROLL_RIGHT = 4
    STACK = 5
    EXPAND = 6
    LASER = 7


class Align(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2