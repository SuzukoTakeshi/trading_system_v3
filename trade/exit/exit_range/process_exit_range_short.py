#
# trade/exit/exit_range/process_exit_range_short.py
#
# Exit Range Process Short
#
# 役割:
#   ・SHORTのRANGE EXIT管理
#   ・RANGE EXIT判定
#

from core.logger import Log

from trade.trade_enums import ExitReason

from trade.exit.process_exit_base import ProcessExitBase
from trade.range_boundary import confirm_boundary_duration


class ProcessExitRangeShort(ProcessExitBase):

    def __init__(self, context, market):

        super().__init__(context, market)

        Log.create("ProcessExitRangeShort")

    # ==========================================
    # RANGE EXIT判定
    # ==========================================
    def process(self, trade):

        Log.flow(
            f"(#{trade.id}) ProcessExitRangeShort:process"
        )

        quote = trade.get_quote()
        current_price = quote.current_price

        runtime = trade.runtime.strategy_runtime
        boundary = confirm_boundary_duration(
            trade,
            runtime,
            quote.current_datetime,
            current_price,
        )

        # RANGE上限を超えた場合は、SHORTポジションを終了する。
        if boundary == "upper":
            message = (
                "RANGE UPPER EXIT SHORT: 許容境界外が継続 "
                f"current_price={current_price} "
                f"range_upper_limit={runtime.range_upper_limit} "
                f"confirm_minutes={runtime.boundary_confirm_minutes}"
            )
            trade.message = message

            Log.event(f"(#{trade.id}) {message}")
            trade.add_timeline(
                event="EXIT",
                message=message,
                current_price=current_price,
            )
            trade.runtime.set_exit(
                current_price,
                ExitReason.RANGE_BOUNDARY_EXIT,
            )
            self.notify(trade, "RANGE EXIT SHORT")
            return True

        # RANGE EXIT判定
        if current_price <= runtime.short_exit_lower:
            message = (
                f"RANGE EXIT SHORT "
                f"current_price={current_price} "
                f"<= exit_price={runtime.short_exit_lower}"
            )

            Log.event(f"(#{trade.id}) {message}")

            trade.add_timeline(
                event="EXIT",
                message=message,
                current_price=current_price,
            )

            trade.runtime.set_exit(
                current_price,
                ExitReason.RANGE_EXIT,
            )

            self.notify(
                trade,
                "RANGE EXIT SHORT",
            )

            return True

        return False
