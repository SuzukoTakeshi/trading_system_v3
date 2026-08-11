#
# models/trade/trade_chart_data.py
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


class TradeChartData:

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
        )
