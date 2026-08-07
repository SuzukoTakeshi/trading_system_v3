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

from core.logger import Log

from config.strategy_config_loader import StrategyConfig

from trade.process.process_base import ProcessBase


class ProcessEntryBase(ProcessBase):

    def __init__(self, context, market):

        super().__init__(
            context,
            market
        )

        self.strategy_config = StrategyConfig.instance()

        self.trade = None
        self.quote = None

    #
    # 共通PROCESS
    #
    def process_base(self, trade, quote):

        self.trade = trade
        self.quote = quote

        price = quote.price
        if price is None:
            return

        if (
            trade.runtime.trailing_highest_price is None
            or price > trade.runtime.trailing_highest_price
        ):
            trade.runtime.trailing_highest_price = price

        if (
            trade.runtime.trailing_lowest_price is None
            or price < trade.runtime.trailing_lowest_price
        ):
            trade.runtime.trailing_lowest_price = price

    #
    # ENTRY Timeline追加
    #
    def add_entry_timeline(self, message):

        self.trade.add_timeline(
            type="ENTRY",
            message=message
        )

    #
    # Strategy設定取得
    #
    def get_entry_config(self):

        return (
            self.strategy_config
            .get_strategy(
                self.trade.param.strategy.value
            )
            ["entry"]
        )
