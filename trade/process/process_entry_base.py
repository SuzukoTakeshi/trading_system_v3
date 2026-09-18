#
# trade/process/process_entry_base.py
#
# Entry Process Base
#
# 役割:
#   ・LONG/SHORT共通処理
#   ・ENTRY基盤
#
# 注意:
#   ・売買条件は実装しない
#   ・LONG/SHORT側で実装する
#

from core.strategy_config_loader import StrategyConfig

from trade.process.process_base import ProcessBase


class ProcessEntryBase(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        self.strategy_config = StrategyConfig.instance()

        self.trade = None
        self.quote = None

    # ==========================================
    # 共通PROCESS
    # ==========================================
    def process_base(self, trade, quote):

        self.trade = trade
        self.quote = quote

        current_price = quote.current_price
        if current_price is None:
            return

        if (
            trade.runtime.trailing_highest_price is None
            or current_price > trade.runtime.trailing_highest_price
        ):
            trade.runtime.trailing_highest_price = current_price

        if (
            trade.runtime.trailing_lowest_price is None
            or current_price < trade.runtime.trailing_lowest_price
        ):
            trade.runtime.trailing_lowest_price = current_price


    # ==========================================
    # Strategy設定取得
    # ==========================================
    def get_entry_config(self):
        return (
            self.strategy_config
            .get_strategy(self.trade.param.strategy.value)
            ["entry"]
        )
