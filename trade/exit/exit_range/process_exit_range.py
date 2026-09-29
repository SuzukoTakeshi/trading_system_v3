#
# trade/exit/exit_range/process_exit_range.py
#
# Exit Range Process
#
# 役割:
#   ・RANGE EXIT判定を統括する
#   ・LONG/SHORTに応じたRANGE EXIT判定処理を呼び出す
#
# 注意:
#   ・Trade状態の変更は行わない
#   ・EXIT注文は生成しない
#

from core.exception import InternalError
from core.logger import Log

from trade.trade_enums import SideType

from trade.exit.exit_range.process_exit_range_long import (
    ProcessExitRangeLong,
)
from trade.exit.exit_range.process_exit_range_short import (
    ProcessExitRangeShort,
)


class ProcessExitRange:

    def __init__(self, context, market):

        Log.create("ProcessExitRange")

        self.context = context
        self.market = market

        self.long = ProcessExitRangeLong(context, market)
        self.short = ProcessExitRangeShort(context, market)

    # ==========================================
    # RANGE EXIT判定
    # ==========================================
    def process(self, trade):

        Log.flow(f"(#{trade.id}) ProcessExitRange:process")

        runtime = trade.runtime.strategy_runtime

        if (runtime.long_exit_upper is None or runtime.short_exit_lower is None):
            self._update_params(runtime)

        if trade.param.side == SideType.LONG:
            return self.long.process(trade)

        if trade.param.side == SideType.SHORT:
            return self.short.process(trade)

        raise InternalError(
            message=f"UNKNOWN SIDE {trade.param.side}",
            code="UNKNOWN_SIDE",
        )


    # ==========================================
    # RANGE EXITパラメータ更新
    # ==========================================
    def _update_params(self, runtime):

        range_width = (
            runtime.range_high - runtime.range_low
        )

        # LONG EXIT
        long_deviation = (
            range_width
            * runtime.exit_high_deviation_rate
            / 100
        )

        runtime.long_exit_upper = (
            runtime.range_high - long_deviation
        )

        # SHORT EXIT
        short_deviation = (
            range_width
            * runtime.exit_low_deviation_rate
            / 100
        )

        runtime.short_exit_lower = (
            runtime.range_low + short_deviation
        )
