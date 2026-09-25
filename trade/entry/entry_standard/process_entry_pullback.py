#
# trade/entry/entry_standard/process_entry_pullback.py
#
# Entry Pullback Process
#
# 役割:
#   ・STANDARD ENTRYのPullback判定
#   ・LONG / SHORTのPullback判定を呼び出す
#   ・Pullback成立結果を返す
#
# 注意:
#   ・Trade状態の変更は行わない
#   ・ENTRY注文は生成しない
#

from core.exception import InternalError
from core.logger import Log

from trade.trade_enums import SideType

from trade.entry.entry_standard.process_entry_pullback_long import (
    ProcessEntryPullbackLong,
)
from trade.entry.entry_standard.process_entry_pullback_short import (
    ProcessEntryPullbackShort,
)


class ProcessEntryPullback:

    def __init__(self, context, market):

        Log.create("ProcessEntryPullback")

        self.context = context
        self.market = market

        self.long = ProcessEntryPullbackLong(context, market)
        self.short = ProcessEntryPullbackShort(context, market)

    # ==========================================
    # Pullback判定
    # ==========================================
    def process(self, trade):

        Log.flow(
            f"(#{trade.id}) ProcessEntryPullback:process"
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