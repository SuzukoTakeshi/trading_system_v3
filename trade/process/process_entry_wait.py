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


class ProcessEntryWait(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessEntryWait")


    def process(self, trade):

        Log.flow(f"(#{trade.id}) ProcessEntryWait:process")

        quote = trade.runtime.quote
        current_price = quote.current_price

        # 初回価格取得完了
        trade.runtime.entry_previous_price = current_price

        Log.event(
            f"(#{trade.id}) ENTRY WAIT COMPLETE "
            f"symbol={trade.param.symbol} "
            f"current_price={current_price}"
        )

        return True