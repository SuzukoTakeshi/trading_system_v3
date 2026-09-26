#
# trade/exit/exit_stop/process_exit_stop_base.py
#
# Exit Stop Process Base
#
# 役割:
#   ・STOP EXIT共通処理
#   ・LONG/SHORT共通処理
#   ・ENTRY約定確認
#   ・初期STOP待機
#
# 注意:
#   ・LONG/SHORT固有のSTOP計算は実装しない
#   ・LONG/SHORT側で実装する
#

from datetime import datetime, timedelta

from core.exception import EntryPriceNotFoundError
from core.logger import Log

from trade.exit.process_exit_base import ProcessExitBase


class ProcessExitStopBase(ProcessExitBase):

    def __init__(self, context, market):

        super().__init__(context, market)

        Log.create("ProcessExitStopBase")

    # ==========================================
    # ENTRY約定確認
    # ==========================================
    def check_entry_price(self, trade):

        if (
            trade.entry_order is None
            or trade.entry_order.result is None
            or trade.entry_order.result.price is None
        ):
            raise EntryPriceNotFoundError(
                message=f"({trade.id}) ENTRY PRICE NOT FOUND",
                code="ENTRY_PRICE_NOT_FOUND",
            )

    # ==========================================
    # 初期STOP待機
    # ==========================================
    def is_initial_stop_delay(self, trade):

        delay_seconds = trade.param.initial_stop_delay_seconds

        if delay_seconds <= 0:
            return False

        stop_delay_time = (
            trade.runtime.stop_start_time
            + timedelta(seconds=delay_seconds)
        )

        if datetime.now() < stop_delay_time:

            Log.debug(
                f"(#{trade.id}) INITIAL STOP WAIT "
                f"delay={delay_seconds}s"
            )

            return True

        return False
