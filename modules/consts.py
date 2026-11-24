"""Program consts"""
from enum import Enum


class SettingsParams(Enum):
    """Settings parametrs enum"""
    COUNT = "count"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    HEIGHT = "height"
    WIDTH = "width"
    MIN_SPEED = "min_speed"
    MAX_SPEED = "max_speed"
    USE_COLOR = "use_color"


class ButtonNames(Enum):
    """Buttons names enum"""
    START = "start"
    STOP = "stop"
    RESTART = "restart"


base_settings = {
    SettingsParams.COUNT.value: 20,
    SettingsParams.MIN_VALUE.value: 10,
    SettingsParams.MAX_VALUE.value: 30,
    SettingsParams.HEIGHT.value: 560,
    SettingsParams.WIDTH.value: 800,
    SettingsParams.MIN_SPEED.value: 4,
    SettingsParams.MAX_SPEED.value: 10,
    SettingsParams.USE_COLOR.value: True
}

MAX_LEFT_GRID = 1
SPEED = 60
CAPACITY = 2
