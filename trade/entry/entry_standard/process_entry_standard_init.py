#
# trade/entry/entry_standard/process_entry_standard_init.py
#
# STANDARD Entry Init
#
# 役割:
#   ・STANDARD ENTRY開始時の初期化
#

from core.logger import Log

from trade.process.process_base import ProcessBase


class ProcessEntryStandardInit(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)
        Log.create("ProcessEntryStandardInit")

    def process(self, trade):
        Log.flow(
            f"(#{trade.id}) ProcessEntryStandardInit:process"
        )

        quote = trade.get_quote()
        current_price = quote.current_price

        runtime = trade.runtime.strategy_runtime

        # ENTRY判定の基準価格
        runtime.entry_base_price = current_price

        # ENTRY判定開始時点の直前価格
        runtime.entry_previous_price = current_price

        Log.event(
            f"(#{trade.id}) STANDARD初期価格設定 "
            f"symbol={trade.param.symbol} "
            f"entry_base_price={runtime.entry_base_price}"
        )

        return True