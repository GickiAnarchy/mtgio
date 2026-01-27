from .setsscreen import SetsScreen
from .mainscreen import MainScreen


ALL_SCREENS = [
    (SetsScreen, "sets"),
    (MainScreen, "main"),
]



__all__ = [
    "SetsScreen",
    "MainScreen",
    "ALL_SCREENS",
]