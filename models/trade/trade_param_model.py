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
    MarginType,
    SideType,
    StrategyType,
)

class TradeParamModel:

    def __init__(
        self,
        strategy_type,

        symbol,
        quantity,
        trade_price,
        atr,
        trade_type,
        margin_type,
        side,
        strategy,
        params,

        initial_stop_delay_seconds,
        stop_atr_multiplier,
        trail_atr_multiplier,
        time_enabled,
        time_limit_minutes,
        close_enabled,
        close_time,

        # チャートデータ保存間隔
        chart_interval_seconds,

        repeat_count=1,
        repeat_index=1,
        repeat_group_id=None,
        entry_method=None,
        exit_method="stop",
    ):

        # 戦略タイプ
        self.strategy_type = strategy_type

        # RANGE以外のENTRY/EXIT判定方式
        if entry_method == "standard":
            entry_method = "pullback_reversal"
        self.entry_method = entry_method or (
            "pullback_reversal"
            if strategy_type == "standard"
            else strategy_type
        )
        self.exit_method = exit_method or "stop"

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

        # 戦略パラメータ
        self.params = params

        # EXIT設定
        self.initial_stop_delay_seconds = initial_stop_delay_seconds
        self.stop_atr_multiplier = stop_atr_multiplier
        self.trail_atr_multiplier = trail_atr_multiplier
        self.time_enabled = time_enabled
        self.time_limit_minutes = time_limit_minutes
        self.close_enabled = close_enabled
        self.close_time = close_time

        self.chart_interval_seconds = chart_interval_seconds

        # RANGE連続売買
        self.repeat_count = repeat_count
        self.repeat_index = repeat_index
        self.repeat_group_id = repeat_group_id

        # ---------------------------------------
        # MarketDes
        # ---------------------------------------
        # Trade開始時に取得した銘柄の市場情報
        #
        # Trade実行中は変更しない。
        #
        # 売買単位
        self.trading_unit = None

        # 制限値幅下限
        self.lower_limit = None

        # 制限値幅上限
        self.upper_limit = None


    def to_dict(self):

        return {
            "strategy_type": self.strategy_type,
            "entry_method": self.entry_method,
            "exit_method": self.exit_method,

            "symbol": self.symbol,
            "quantity": self.quantity,
            "trade_price": self.trade_price,
            "atr": self.atr,

            "trade_type": self.trade_type.value,
            "margin_type": self.margin_type,
            "side": self.side.value,
            "strategy": self.strategy.value,
            "params": self.params,

            "initial_stop_delay_seconds": self.initial_stop_delay_seconds,
            "stop_atr_multiplier": self.stop_atr_multiplier,
            "trail_atr_multiplier": self.trail_atr_multiplier,
            "time_enabled": self.time_enabled,
            "time_limit_minutes": self.time_limit_minutes,
            "close_enabled": self.close_enabled,
            "close_time": self.close_time,

            "chart_interval_seconds": self.chart_interval_seconds,

            "repeat_count": self.repeat_count,
            "repeat_index": self.repeat_index,
            "repeat_group_id": self.repeat_group_id,

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
            strategy_type=data.get("strategy_type", "standard"),
            entry_method=data.get("entry_method"),
            exit_method=data.get("exit_method", "stop"),

            symbol=data.get("symbol"),
            quantity=data.get("quantity"),
            trade_price=data.get("trade_price"),
            atr=data.get("atr"),
            trade_type=TradeType(data.get("trade_type")),
            margin_type=MarginType(data.get("margin_type")),
            side=SideType(data.get("side")),
            strategy=StrategyType(data.get("strategy")),
            params=data.get("params", {}),

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

            repeat_count=data.get("repeat_count", 1),
            repeat_index=data.get("repeat_index", 1),
            repeat_group_id=data.get("repeat_group_id"),
        )
