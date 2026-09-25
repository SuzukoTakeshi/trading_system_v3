#
# trade/entry/entry_standard/process_entry_reversal.py
#
# Entry Reversal Process
#
# 役割:
#   ・STANDARD ENTRYのReversal判定
#   ・LONG / SHORTのReversal判定を呼び出す
#   ・Reversal成立結果を返す
#
# 注意:
#   ・Trade状態の変更を行う
#   ・TradeRuntimeを更新する
#   ・Timeline / Notifyを行う
#   ・ENTRY注文は生成しない
#

from core.exception import InternalError
from core.logger import Log

from trade.entry.entry_standard.process_entry_reversal_long import (
    ProcessEntryReversalLong,
)
from trade.entry.entry_standard.process_entry_reversal_short import (
    ProcessEntryReversalShort,
)
from trade.trade_enums import SideType


class ProcessEntryReversal:

    def __init__(self, context, market):

        Log.create("ProcessEntryReversal")

        self.context = context
        self.market = market

        self.long = ProcessEntryReversalLong(
            context,
            market,
        )

        self.short = ProcessEntryReversalShort(
            context,
            market,
        )

    # ==========================================
    # Reversal判定
    # ==========================================
    def process(self, trade):

        Log.flow(
            f"(#{trade.id}) ProcessEntryReversal:process"
        )

        if trade.param.side == SideType.LONG:

            return self.long.process(trade)

        elif trade.param.side == SideType.SHORT:

            return self.short.process(trade)

        else:

            raise InternalError(
                message=f"UNKNOWN SIDE {trade.param.side}",
                code="UNKNOWN_SIDE",
            )