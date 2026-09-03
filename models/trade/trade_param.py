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

from trade.trade_enums import (
    TradeType,
    SideType,
    StrategyType,
)

class TradeParam:

    def __init__(
        self,
        symbol,
        quantity,
        trade_price,
        atr,
        trade_type,
        margin_type,
        side,
        strategy,

        initial_stop_delay_seconds,
        stop_atr_multiplier,
        trail_atr_multiplier,
        time_enabled,
        time_limit_minutes,
        close_enabled,
        close_time,

        # チャートデータ保存間隔
        chart_interval_seconds,
    ):

        # 銘柄
        self.symbol = symbol

        # 数量
        self.quantity = quantity

        # 登録価格
        self.trade_price = trade_price

        # ENTRY時ATR
        self.atr = atr

        # 取引情報 (現物/信用)
        self.trade_type = trade_type

        # 信用区分 (制度(6ヶ月)/一般(無期限)/一般(14日)/一般(1日))
        self.margin_type = margin_type

        self.side = side

        # 戦略 (スキャルピング/デイトレ/スウィング)
        self.strategy = strategy

        # EXIT設定
        self.initial_stop_delay_seconds = initial_stop_delay_seconds
        self.stop_atr_multiplier = stop_atr_multiplier
        self.trail_atr_multiplier = trail_atr_multiplier
        self.time_enabled = time_enabled
        self.time_limit_minutes = time_limit_minutes
        self.close_enabled = close_enabled
        self.close_time = close_time

        self.chart_interval_seconds = chart_interval_seconds

        # MarketDes
        # 銘柄の市場情報

        # 売買単位
        self.trading_unit = None

        # 制限値幅下限
        self.lower_limit = None

        # 制限値幅上限
        self.upper_limit = None


    def to_dict(self):

        return {
            "symbol": self.symbol,
            "quantity": self.quantity,
            "trade_price": self.trade_price,
            "atr": self.atr,

            "trade_type": self.trade_type.value,
            "margin_type": self.margin_type,
            "side": self.side.value,
            "strategy": self.strategy.value,

            "initial_stop_delay_seconds": self.initial_stop_delay_seconds,
            "stop_atr_multiplier": self.stop_atr_multiplier,
            "trail_atr_multiplier": self.trail_atr_multiplier,
            "time_enabled": self.time_enabled,
            "time_limit_minutes": self.time_limit_minutes,
            "close_enabled": self.close_enabled,
            "close_time": self.close_time,

            "chart_interval_seconds": self.chart_interval_seconds,

            # MarketDes
            "trading_unit": self.trading_unit,
            "lower_limit": self.lower_limit,
            "upper_limit": self.upper_limit,
        }


    def set_market_des(self, data):
        """
        MarketDesデータを設定
        """
        self.trading_unit = data.get("trading_unit")
        self.lower_limit = data.get("lower_limit")
        self.upper_limit = data.get("upper_limit")


    @classmethod
    def from_dict(cls, data):

        return cls(
            symbol=data.get("symbol"),
            quantity=data.get("quantity"),
            trade_price=data.get("trade_price"),
            atr=data.get("atr"),
            trade_type=TradeType(data.get("trade_type")),
            margin_type=data.get("margin_type"),
            side=SideType(data.get("side")),
            strategy=StrategyType(data.get("strategy")),

            initial_stop_delay_seconds=(data.get("initial_stop_delay_seconds", 0)),
            stop_atr_multiplier=(data.get("stop_atr_multiplier", 0)),
            trail_atr_multiplier=(data.get("trail_atr_multiplier", 0)),
            time_enabled=(data.get("time_enabled", False)),
            time_limit_minutes=(data.get("time_limit_minutes", 0)),
            close_enabled=(data.get("close_enabled", False)),
            close_time=(data.get("close_time", "15:15")),

            chart_interval_seconds=(
                data.get("chart_interval_seconds", 5)
            ),
        )
