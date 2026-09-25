#
# trade/entry/entry_standard/process_entry_standard.py
#
# Entry Standard Process
#
# 役割:
#   ・STANDARD ENTRY条件を判定する
#   ・Pullback / ReversalのENTRY判定を統括する
#
# 注意:
#   ・Trade状態の変更は行わない
#   ・EntryStateを更新する
#   ・TradeRuntimeを更新する
#   ・Timeline / Notifyを行う
#   ・ENTRY注文は生成しない
#

from core.exception import InternalError
from core.logger import Log

from trade.entry.entry_standard.process_entry_pullback import (
    ProcessEntryPullback,
)
from trade.entry.entry_standard.process_entry_reversal import (
    ProcessEntryReversal,
)
from trade.trade_enums import EntryState


class ProcessEntryStandard:

    def __init__(self, context, market):

        Log.create("ProcessEntryStandard")

        self.context = context
        self.market = market

        self.entry_pullback = ProcessEntryPullback(
            context,
            market,
        )

        self.entry_reversal = ProcessEntryReversal(
            context,
            market,
        )

    # ==========================================
    # STANDARD ENTRY判定
    # ==========================================
    def process(self, trade):

        Log.flow(
            f"(#{trade.id}) ProcessEntryStandard:process"
        )


        # ==========================================
        # Pullback判定
        # ・Pullback開始待機
        # ・Pullback監視
        # ==========================================
        if trade.entry_state in (
            EntryState.WAITING,
            EntryState.PULLBACK,
        ):

            result = self.entry_pullback.process(trade)

            if result:
                trade.entry_state = EntryState.REVERSAL

            return False

        # ==========================================
        # Reversal判定
        # ==========================================
        if trade.entry_state == EntryState.REVERSAL:

            return self.entry_reversal.process(trade)

        raise InternalError(
            message=f"UNKNOWN ENTRY STATE {trade.entry_state}",
            code="UNKNOWN_ENTRY_STATE",
        )