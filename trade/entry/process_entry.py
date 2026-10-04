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
from trade.entry.entry_range.process_entry_range import ProcessEntryRange
from trade.entry.entry_trend.process_entry_trend import ProcessEntryTrend
from trade.entry.entry_trend.process_entry_trend2 import ProcessEntryTrend2

class ProcessEntry:

    def __init__(self, context, market):

        Log.create("ProcessEntry")

        self.context = context
        self.market = market

        self.entry_standard = ProcessEntryStandard(context, market)
        self.entry_range = ProcessEntryRange(context, market)
        self.entry_trend = ProcessEntryTrend()
        self.entry_trend2 = ProcessEntryTrend2(context, market)


    # ==========================================
    # ENTRY判定
    # ==========================================
    def process(self, trade):

        # Log.flow(f"(#{trade.id}) ProcessEntry:process")

        if trade.param.strategy_type == "standard":
            if trade.param.entry_method == "pullback_reversal":
                return self.entry_standard.process(trade)
            if trade.param.entry_method == "immediate":
                return True

        if trade.param.strategy_type == "range":
            return self.entry_range.process(trade)

        if trade.param.strategy_type == "trend":
            self.entry_trend.update(trade)
            return False

        if trade.param.strategy_type == "trend2":
            return self.entry_trend2.process(trade)

        return False
