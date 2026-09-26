#
# trade/exit/exit_stop/process_exit_stop_short.py
#
# Exit Stop Process Short
#
# 役割:
#   ・SHORTのSTOP EXIT管理
#   ・初期STOP設定
#   ・STOP更新
#   ・STOP判定
#

from datetime import datetime

from core.logger import Log

from trade.exit.exit_stop.process_exit_stop_base import (
    ProcessExitStopBase,
)

from trade.trade_enums import ExitReason


class ProcessExitStopShort(ProcessExitStopBase):

    def __init__(self, context, market):

        super().__init__(context, market)

        Log.create("ProcessExitStopShort")

    # ==========================================
    # STOP EXIT判定
    # ==========================================
    def process(self, trade):

        Log.flow(
            f"(#{trade.id}) ProcessExitStopShort:process"
        )

        self.trade = trade
        self.quote = trade.get_quote()

        # ENTRY約定確認
        self.check_entry_price(trade)

        # 初回STOP初期化
        if trade.runtime.stop_price is None:
            self.init_stop(trade)

            return False

        # 初期STOP待機
        if self.is_initial_stop_delay(trade):
            return False

        # STOP更新
        self.update_stop(trade)

        # STOP判定
        return self.is_stop_hit(trade)

    # ==========================================
    # STOP初期化
    # ==========================================
    def init_stop(self, trade):

        trade.runtime.stop_start_time = datetime.now()
        trade.runtime.stop_price = None
        trade.runtime.stop_highest_price = None
        trade.runtime.stop_lowest_price = None

        entry_price = trade.entry_order.result.price
        atr_amount = entry_price * trade.param.atr / 100

        # ENTRY約定価格を基準にATR(%)から初期STOP価格を設定する
        trade.runtime.stop_price = (
            entry_price
            + atr_amount * trade.param.stop_atr_multiplier
        )

        trade.runtime.stop_lowest_price = entry_price
        trade.runtime.stop_highest_price = None

        # 初期STOP
        message = (
            f"INITIAL STOP "
            f"entry={entry_price} "
            f"stop={trade.runtime.stop_price}"
        )

        Log.event(f"(#{trade.id}) {message}")

        trade.add_timeline(
            event="STOP",
            message=message,
            current_price=entry_price,
        )

        # 通知
        self.notify(trade, "INIT STOP SHORT")

    # ==========================================
    # 安値更新
    # ==========================================
    def update_stop(self, trade):

        current_price = self.quote.current_price

        if (
            trade.runtime.stop_lowest_price is None
            or current_price < trade.runtime.stop_lowest_price
        ):

            trade.runtime.stop_lowest_price = current_price

            message = (
                f"STOP LOW UPDATE SHORT "
                f"current_price={current_price}"
            )

            Log.event(f"(#{trade.id}) {message}")

            trade.add_timeline(
                event="STOP",
                message=message,
                current_price=current_price,
            )

            entry_price = trade.entry_order.result.price
            atr_amount = entry_price * trade.param.atr / 100

            new_stop = (
                trade.runtime.stop_lowest_price
                + atr_amount * trade.param.trail_atr_multiplier
            )

            if new_stop < trade.runtime.stop_price:

                trade.runtime.stop_price = new_stop

                message = (
                    f"STOP UPDATE SHORT "
                    f"current_price={current_price} "
                    f"stop={trade.runtime.stop_price}"
                )

                Log.event(f"(#{trade.id}) {message}")

                trade.add_timeline(
                    event="STOP",
                    message=message,
                    current_price=current_price,
                )

    # ==========================================
    # STOP判定
    # ==========================================
    def is_stop_hit(self, trade):

        current_price = self.quote.current_price

        if current_price >= trade.runtime.stop_price:

            message = (
                f"STOP HIT SHORT "
                f"current_price={current_price} "
                f">= stop_price={trade.runtime.stop_price}"
            )

            Log.event(f"(#{trade.id}) {message}")

            trade.add_timeline(
                event="EXIT",
                message=message,
                current_price=current_price,
            )

            trade.runtime.set_exit(
                current_price,
                ExitReason.STOP_LINE_EXIT,
            )

            return True

        return False
