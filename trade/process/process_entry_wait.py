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

        # 初回価格設定
        #
        # ENTRY判定の基準価格
        #   trade_price=0   : 初回取得した市場価格
        #   trade_price!=0  : Tradeに指定された開始価格
        #
        if trade.param.trade_price == 0:
            trade.runtime.entry_base_price = current_price
        else:
            trade.runtime.entry_base_price = trade.param.trade_price

        # ENTRY判定開始時点の直前価格
        #
        # 連続上昇・下降判定で使用する。
        #
        trade.runtime.entry_previous_price = current_price

        Log.event(
            f"(#{trade.id}) 初回価格設定 symbol={trade.param.symbol} "
            f"entry_base_price={trade.runtime.entry_base_price}"
        )

        # 通知
        self.notify(trade, "ENTRY WAIT")

        return True
