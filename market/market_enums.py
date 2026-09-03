#
# market/market_enums.py
#
# Market Enums
#

from enum import Enum


class MarketSessionEvent(str, Enum):

    MORNING_OPEN = "MORNING_OPEN"
    MORNING_CLOSE = "MORNING_CLOSE"
    AFTERNOON_OPEN = "AFTERNOON_OPEN"
    AFTERNOON_CLOSE = "AFTERNOON_CLOSE"