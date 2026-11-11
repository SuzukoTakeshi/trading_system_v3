
#
# models/trade/trend_bar_model.py
#
# Trend Bar
#
# 役割:
#   ・OHLCVデータ管理
#   ・移動平均データ管理
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
        volume=0,
        ma_short=None,
        ma_medium=None,
        ma_long=None,
    ):
        self.time = time or datetime.now()
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume if volume is not None else 0

        # RSS移動平均
        self.ma_short = ma_short
        self.ma_medium = ma_medium
        self.ma_long = ma_long

    def to_dict(self):
        return {
            "time": self.time.isoformat() if self.time else None,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "ma_short": self.ma_short,
            "ma_medium": self.ma_medium,
            "ma_long": self.ma_long,
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
            volume=data.get("volume", 0),
            ma_short=data.get("ma_short"),
            ma_medium=data.get("ma_medium"),
            ma_long=data.get("ma_long"),
        )
