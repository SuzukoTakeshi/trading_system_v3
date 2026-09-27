#
# trade/entry/process_entry.py
#
# Entry Process
#
# 役割:
#   ・ENTRY判定の唯一の入口
#   ・ENTRY条件に応じた判定処理を呼び出す
#   ・条件成立結果を返す
#
# 注意:
#   ・Trade状態の変更は行わない
#   ・ENTRY注文は生成しない
#

from core.logger import Log

from trade.entry.entry_standard.process_entry_standard import ProcessEntryStandard
from trade.entry.entry_pass.process_entry_pass import ProcessEntryPass
from trade.entry.entry_range.process_entry_range import ProcessEntryRange

class ProcessEntry:

    def __init__(self, context, market):

        Log.create("ProcessEntry")

        self.context = context
        self.market = market

        self.entry_standard = ProcessEntryStandard(context, market)
        self.entry_pass = ProcessEntryPass(context, market)
        self.entry_range = ProcessEntryRange(context, market)

    # ==========================================
    # ENTRY判定
    # ==========================================
    def process(self, trade):

        # Log.flow(f"(#{trade.id}) ProcessEntry:process")

        if trade.param.strategy_type == "standard":
            return self.entry_standard.process(trade)

        if trade.param.strategy_type == "pass":
            return self.entry_pass.process(trade)

        if trade.param.strategy_type == "range":
            return self.entry_range.process(trade)

        return False