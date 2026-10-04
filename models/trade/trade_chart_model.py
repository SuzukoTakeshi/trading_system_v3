#
# models/trade/trade_chart_model.py
#
# Trade Chart Data
#
# 役割:
# ・Tradeの推移をチャート表示するための1件のデータを管理
# ・価格、OHLC、Watermark、STOP、ENTRY/EXIT情報等を保持
#

from datetime import datetime

from trade.trade_enums import (
    SideType,
    TradeState,
)


class TradeChartModel:

    def __init__(
        self,
        time=None,

        # Trade情報
        high_watermark=None,
        low_watermark=None,
        stop_loss=None,

        entry_time=None,
        entry_price=None,

        exit_time=None,
        exit_price=None,

        side=None,
        state=None,

        # OHLC
        price_open=None,
        price_high=None,
        price_low=None,
        price_close=None,

        range_params=None,
        trend_direction=None,
        trend_high=None,
        trend_low=None,
        trend_moving_average=None,
    ):

        self.time = time or datetime.now()

        # Trade情報
        self.high_watermark = high_watermark
        self.low_watermark = low_watermark
        self.stop_loss = stop_loss

        self.entry_time = entry_time
        self.entry_price = entry_price

        self.exit_time = exit_time
        self.exit_price = exit_price

        self.side = side
        self.state = state

        # OHLC
        self.price_open = price_open
        self.price_high = price_high
        self.price_low = price_low
        self.price_close = price_close

        # RANGE
        self.range_params = range_params
        self.trend_direction = trend_direction
        self.trend_high = trend_high
        self.trend_low = trend_low
        self.trend_moving_average = trend_moving_average
        # {
        #     "range_high": 3060.0,
        #     "range_low": 2975.0,
        #     "long_entry_upper": 2993.125,
        #     "short_entry_lower": 3041.875,
        #     "range_upper_limit": 3078.125,
        #     "range_lower_limit": 2956.875
        # }


    @property
    def price(self):
        """
        現在価格

        OHLCの終値を現在価格として扱う。
        """
        return self.price_close


    def to_dict(self):

        return {
            "time": self.time.isoformat() if self.time else None,

            # Trade情報
            "high_watermark": self.high_watermark,
            "low_watermark": self.low_watermark,
            "stop_loss": self.stop_loss,

            "entry_time": (
                self.entry_time.isoformat()
                if self.entry_time
                else None
            ),
            "entry_price": self.entry_price,

            "exit_time": (
                self.exit_time.isoformat()
                if self.exit_time
                else None
            ),
            "exit_price": self.exit_price,

            "side": self.side.value if self.side else None,
            "state": self.state.value if self.state else None,

            # OHLC
            "price_open": self.price_open,
            "price_high": self.price_high,
            "price_low": self.price_low,
            "price_close": self.price_close,

            # RANGE
            "range_params": self.range_params,
            "trend_direction": self.trend_direction,
            "trend_high": self.trend_high,
            "trend_low": self.trend_low,
            "trend_moving_average": self.trend_moving_average,
        }


    @classmethod
    def from_dict(cls, data):

        return cls(
            time=(
                datetime.fromisoformat(data["time"])
                if data.get("time")
                else None
            ),

            # Trade情報
            high_watermark=data.get("high_watermark"),
            low_watermark=data.get("low_watermark"),
            stop_loss=data.get("stop_loss"),

            entry_time=(
                datetime.fromisoformat(data["entry_time"])
                if data.get("entry_time")
                else None
            ),
            entry_price=data.get("entry_price"),

            exit_time=(
                datetime.fromisoformat(data["exit_time"])
                if data.get("exit_time")
                else None
            ),
            exit_price=data.get("exit_price"),

            side=(
                SideType(data["side"])
                if data.get("side")
                else None
            ),

            state=(
                TradeState(data["state"])
                if data.get("state")
                else None
            ),

            # OHLC
            price_open=data.get("price_open"),
            price_high=data.get("price_high"),
            price_low=data.get("price_low"),
            price_close=data.get("price_close"),

            # RANGE
            range_params=data.get("range_params"),
            trend_direction=data.get("trend_direction"),
            trend_high=data.get("trend_high"),
            trend_low=data.get("trend_low"),
            trend_moving_average=data.get("trend_moving_average"),
        )
