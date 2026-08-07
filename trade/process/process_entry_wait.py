#
# trade/process/process_entry_wait.py
#
# Entry Wait Process
#
# 役割:
#   ・ENTRY判定開始前のMarket準備確認
#   ・初回価格取得待ち
#   ・ENTRY_PULLBACK移行条件判定
#

from core.logger import Log

from trade.process.process_base import ProcessBase

from trade.trade_enums import TradeState


class ProcessEntryWait(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.debug("CREATE ProcessEntryWait")


    def process(self, trade):

        quote = self.context.cache.quotes.get(
            trade.param.symbol
        )

        if quote is None:
            return False


        # 初回価格取得完了
        trade.runtime.entry_previous_price = quote.price

        Log.event(
            f"ENTRY WAIT COMPLETE "
            f"id={trade.id} "
            f"symbol={trade.param.symbol} "
            f"price={quote.price}"
        )

        return True