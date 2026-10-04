#
# models/trade/trend_bar_model.py
#
# Trend Bar
#
# 役割:
#   ・15秒足のOHLCデータ管理
#

from datetime import datetime


class TrendBarModel:

    def __init__(
        self,
        time=None,
        open=None,
        high=None,
        low=None,
        close=None,
    ):
        self.time = time or datetime.now()
        self.open = open
        self.high = high
        self.low = low
        self.close = close

    def to_dict(self):
        return {
            "time": self.time.isoformat() if self.time else None,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
        }

    @classmethod
    def from_dict(cls, data):
        time_str = data.get("time")

        return cls(
            time=datetime.fromisoformat(time_str) if time_str else None,
            open=data.get("open"),
            high=data.get("high"),
            low=data.get("low"),
            close=data.get("close"),
        )