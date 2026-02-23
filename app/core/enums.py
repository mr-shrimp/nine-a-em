from enum import Enum


class Environment(str, Enum):
    DEV = "DEV"
    PAPER = "PAPER"
    LIVE = "LIVE"
    BACKTEST = "BACKTEST"
