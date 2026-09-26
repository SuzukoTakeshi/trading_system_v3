#
# trade/exit/process_exit.py
#
# Exit Process
#
# 役割:
#   ・EXIT判定の唯一の入口
#   ・EXIT条件に応じた判定処理を呼び出す
#   ・条件成立結果を返す
#
# 注意:
#   ・Trade状態の変更は行わない
#   ・EXIT注文は生成しない
#

from datetime import datetime, timedelta

from core.logger import Log

from trade.trade_enums import (
    TradeType,
    MarginType,
    ExitReason,
)

from trade.exit.exit_stop.process_exit_stop import ProcessExitStop


class ProcessExit:

    def __init__(self, context, market):

        Log.create("ProcessExit")

        self.context = context
        self.market = market

        self.exit_stop = ProcessExitStop(context, market)

        self.quote = None

    # ==========================================
    # EXIT判定
    # ==========================================
    def process(self, trade):

        Log.flow(
            f"(#{trade.id}) ProcessExit:process"
        )

        self.quote = trade.get_quote()

        # STOP EXIT
        if self.exit_stop.process(trade):
            return True

        # DEBUGでは時間系EXITを行わない
        if not self.market.is_debug():

            # 1日信用 強制手仕舞い
            if self.is_margin_day_close(trade):
                return True

            # 時間決済
            elif self.is_time_exit(trade):
                return True

            # 指定時刻決済
            elif self.is_close_time_exit(trade):
                return True

        return False

    # ==========================================
    # 1日信用 強制手仕舞い
    # ==========================================
    def is_margin_day_close(self, trade):
        """
        1日信用大引けによる判定
        1日信用取引の強制手仕舞い時刻に到達したかを判定する。
        """

        # 信用取引でない場合は、対象としない。
        if trade.param.trade_type != TradeType.MARGIN:
            return False

        # 1日信用でない場合は、対象としない。
        if trade.param.margin_type != MarginType.DAY:
            return False

        # 市場ルールから1日信用の強制手仕舞い設定を取得する。
        rule = self.context.config["market_rules"]["margin_day_close"]

        # ルール自体が無効の場合は、強制手仕舞いを行わない。
        if not rule["enabled"]:
            return False

        # まだ強制手仕舞い時刻に到達していない場合は、
        # 通常のEXIT監視を継続する。
        now = datetime.now()
        close_time = datetime.strptime(
            rule["time"],
            "%H:%M",
        ).time()

        if now.time() < close_time:
            return False

        # EXIT実績を設定する。
        trade.runtime.set_exit(
            self.quote.current_price,
            ExitReason.MARGIN_DAY_CLOSE,
        )

        message = f"MARGIN DAY CLOSE time={rule['time']}"

        Log.event(f"(#{trade.id}) {message}")

        trade.add_timeline(
            event="EXIT",
            message=message,
        )

        self.notify(
            trade,
            "MARGIN DAY CLOSE",
        )

        return True

    # ==========================================
    # 時間決済
    # ==========================================
    def is_time_exit(self, trade):
        """
        時間決済判定
        ENTRY約定から設定された時間が経過したかを判定する。
        """

        # 時間決済が無効の場合は対象としない。
        if not trade.param.time_enabled:
            return False

        entry_order = trade.entry_order

        if entry_order is None or entry_order.result is None:
            return False

        entry_time = entry_order.result.result_datetime

        # ENTRY約定時刻を基準に、
        # 時間決済を実行する時刻を計算する。
        limit_time = (
            entry_time
            + timedelta(
                minutes=trade.param.time_limit_minutes
            )
        )

        # 現在時刻が時間制限時刻以降になった場合、
        # 時間決済条件成立とする。
        if datetime.now() >= limit_time:

            trade.runtime.set_exit(
                self.quote.current_price,
                ExitReason.TIME_EXIT,
            )

            message = (
                f"TIME LIMIT EXIT "
                f"time_limit_minutes="
                f"{trade.param.time_limit_minutes}min"
            )

            Log.event(f"(#{trade.id}) {message}")

            trade.add_timeline(
                event="EXIT",
                message=message,
            )

            self.notify(
                trade,
                "TIME LIMIT EXIT",
            )

            return True

        return False

    # ==========================================
    # 指定時刻決済
    # ==========================================
    def is_close_time_exit(self, trade):
        """
        指定時刻決済
        指定された時刻に到達したかを判定する。
        """

        # 指定時刻決済が無効の場合は対象としない。
        if not trade.param.close_enabled:
            return False

        # 指定時刻を取得する。
        close_time = datetime.strptime(
            trade.param.close_time,
            "%H:%M",
        ).time()

        now = datetime.now()

        # 現在時刻が指定時刻以降になった場合、
        # 指定時刻決済条件成立とする。
        if now.time() >= close_time:

            trade.runtime.set_exit(
                self.quote.current_price,
                ExitReason.CLOSE_EXIT,
            )

            message = (
                f"TRADE CLOSE TIME EXIT "
                f"close_time={trade.param.close_time}"
            )

            Log.event(f"(#{trade.id}) {message}")

            trade.add_timeline(
                event="EXIT",
                message=message,
            )

            self.notify(
                trade,
                "TRADE CLOSE TIME EXIT",
            )

            return True

        return False
