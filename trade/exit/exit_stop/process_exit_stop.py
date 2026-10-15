#
# trade/exit/exit_stop/process_exit_stop.py
#
# Exit Stop Process
#
# 役割:
#   ・STOP EXIT判定を統括する
#   ・LONG/SHORTに応じたSTOP判定処理を呼び出す
#
# 注意:
#   ・Trade状態の変更は行わない
#   ・EXIT注文は生成しない
#

from core.logger import Log
from core.exception import StrategySideDisabledError

from trade.trade_enums import SideType

from trade.exit.exit_stop.process_exit_stop_long import (
    ProcessExitStopLong,
)
from trade.exit.exit_stop.process_exit_stop_short import (
    ProcessExitStopShort,
)


class ProcessExitStop:

    def __init__(self, context, market):

        Log.create("ProcessExitStop")

        self.context = context
        self.market = market

        self.long = ProcessExitStopLong(context, market)
        self.short = ProcessExitStopShort(context, market)

    # ==========================================
    # STOP EXIT判定
    # ==========================================
    def process(self, trade):

        Log.flow(f"(#{trade.id}) ProcessExitStop:process")

        side = trade.param.side

        if side == SideType.JUDGE:
            side = trade.runtime.strategy_runtime.trend_side

        if side == SideType.LONG:
            return self.long.process(trade)

        if side == SideType.SHORT:
            return self.short.process(trade)

        raise StrategySideDisabledError(
            message=f"SIDE ERROR(ProcessExitStop) strategy={trade.param.strategy.value} side={side.value}",
            code="SIDE_DISABLED",
        )
