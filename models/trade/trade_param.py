#
# models/trade/trade_param.py
#
# Trade Param
#
# 役割:
#   ・Trade開始時に決定するパラメータ管理
#
#   実行中に変化しない情報を保持する。
#

class TradeParam:

    def __init__(
        self,
        symbol,
        price,
        quantity,
        atr,
        trade_type,
        side,
        strategy,

        initial_stop_delay_seconds,
        stop_atr_multiplier,
        trail_atr_multiplier,
        time_enabled,
        time_limit_minutes,
        close_enabled,
        close_time,
    ):

        # 銘柄
        self.symbol = symbol

        # 登録価格
        self.price = price

        # 数量
        self.quantity = quantity

        # ENTRY時ATR
        self.atr = atr

        # 取引情報
        self.trade_type = trade_type
        self.side = side

        # 戦略
        self.strategy = strategy

        # EXIT設定
        self.initial_stop_delay_seconds = initial_stop_delay_seconds
        self.stop_atr_multiplier = stop_atr_multiplier
        self.trail_atr_multiplier = trail_atr_multiplier
        self.time_enabled = time_enabled
        self.time_limit_minutes = time_limit_minutes
        self.close_enabled = close_enabled
        self.close_time = close_time


    def to_dict(self):

        return {
            "symbol": self.symbol,
            "price": self.price,
            "quantity": self.quantity,
            "atr": self.atr,

            "trade_type": self.trade_type.value,
            "side": self.side.value,
            "strategy": self.strategy.value,

            "initial_stop_delay_seconds": self.initial_stop_delay_seconds,
            "stop_atr_multiplier": self.stop_atr_multiplier,
            "trail_atr_multiplier": self.trail_atr_multiplier,
            "time_enabled": self.time_enabled,
            "time_limit_minutes": self.time_limit_minutes,
            "close_enabled": self.close_enabled,
            "close_time": self.close_time,
        }


    @classmethod
    def from_dict(cls, data):

        from trade.trade_enums import (
            TradeType,
            SideType,
            StrategyType,
        )

        return cls(
            symbol=data.get("symbol"),
            price=data.get("price"),
            quantity=data.get("quantity"),
            atr=data.get("atr"),
            trade_type=TradeType(data.get("trade_type")),
            side=SideType(data.get("side")),
            strategy=StrategyType(data.get("strategy")),

            initial_stop_delay_seconds=(data.get("initial_stop_delay_seconds", 0)),
            stop_atr_multiplier=(data.get("stop_atr_multiplier", 0)),
            trail_atr_multiplier=(data.get("trail_atr_multiplier", 0)),
            time_enabled=(data.get("time_enabled", False)),
            time_limit_minutes=(data.get("time_limit_minutes", 0)),
            close_enabled=(data.get("close_enabled", False)),
            close_time=(data.get("close_time", "15:15")),
        )
