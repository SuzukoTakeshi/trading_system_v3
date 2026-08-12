#
# trade/process/process_trailing_base.py
#
# Trailing Base
#
# 役割:
#

from core.logger import Log

from datetime import datetime, timedelta

from trade.process.process_base import ProcessBase

from core.exception import EntryPriceNotFoundError


class ProcessTrailingBase(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.debug("CREATE ProcessTrailingBase")

    def process(self, trade):

        quote = self.context.cache.quotes.get(trade.param.symbol)

        if quote is None:
            return False

        self.price = price = quote.price

        # 現在価格
        trade.runtime.current_price = price

        # 約定価格確認ガード
        if trade.runtime.entry_price is None:
            raise EntryPriceNotFoundError(
                message=f"ENTRY PRICE NOT FOUND trade={trade.id}",
                code="ENTRY_PRICE_NOT_FOUND",
            )

        # 初回TRAILING初期化
        if trade.runtime.stop_price is None:

            self.init_trailing(trade, price)

            Log.event(
                f"INITIAL TRAILING (#{trade.id}) entry={trade.runtime.entry_price} stop={trade.runtime.stop_price}"
            )
            trade.add_timeline(
                type="TRAILING",
                message=f"INITIAL entry={trade.runtime.entry_price} stop={trade.runtime.stop_price}"
            )

            return False

        return True


    #
    # TRAILING初期化
    #
    def init_trailing(self, trade, price):
        # TRAILING管理情報初期化

        trade.runtime.trailing_start_time = datetime.now()

        trade.runtime.stop_price = None

        trade.runtime.trailing_highest_price = None
        trade.runtime.trailing_lowest_price = None


    #
    # STOP監視開始待ち時間処理
    #
    def is_initial_stop_delay(self, trade):

        if trade.param.initial_stop_delay_seconds <= 0:
            return False

        stop_delay_time = (
            trade.runtime.trailing_start_time
            + timedelta(seconds=trade.param.initial_stop_delay_seconds)
        )

        if datetime.now() < stop_delay_time:
            Log.debug(f"INITIAL STOP DELAY (#{trade.id})")
            return True

        return False


    #
    # 時間決済判定
    #
    def is_time_exit(self, trade):

        if not trade.param.time_enabled:
            return False

        if trade.runtime.entry_time is None:
            return False

        limit_time = trade.runtime.entry_time + timedelta(minutes=trade.param.time_limit_minutes)

        if datetime.now() >= limit_time:

            Log.event(f"TIME EXIT (#{trade.id})")

            trade.runtime.exit_price = self.price
            trade.runtime.exit_time = datetime.now()
            trade.runtime.exit_execution_price = self.price

            trade.add_timeline(
                type="EXIT",
                message=(f"TIME LIMIT {trade.param.time_limit_minutes}min")
            )

            return True

        return False


    #
    # 指定時刻決済判定
    #
    def is_close_time_exit(self, trade):

        if not trade.param.close_enabled:
            return False

        close_time = datetime.strptime(
            trade.param.close_time,
            "%H:%M"
        ).time()

        now = datetime.now()

        if now.time() >= close_time:

            Log.event(
                f"CLOSE TIME EXIT (#{trade.id}) "
                f"time={trade.param.close_time}"
            )

            trade.runtime.exit_price = self.price
            trade.runtime.exit_time = datetime.now()
            trade.runtime.exit_execution_price = self.price

            trade.add_timeline(
                type="EXIT",
                message=(
                    f"CLOSE TIME {trade.param.close_time}"
                )
            )

            return True

        return False
