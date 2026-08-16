#
# trade/process/process_trailing_long.py
#
# Trailing Process Long
#
# 役割:
#   ・保有後のEXIT管理
#   ・初期STOP設定
#   ・STOP更新
#   ・損切り/利確判定
#

from datetime import datetime

from core.logger import Log

from trade.process.process_trailing_base import ProcessTrailingBase


class ProcessTrailingLong(ProcessTrailingBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessTrailingLong")

    #
    # TradeState.TRAILINGで呼ばれる
    #
    def process(self, trade):
        if super().process(trade) == False:
            return False

        price = self.price

        Log.trailing(trade.id,
            f"TRAILING CHECK price={price} "
            f"highest={trade.runtime.trailing_highest_price} stop={trade.runtime.stop_price}"
        )

        # トレーリング更新
        self.update_trailing_stop_price(trade, price)

        result = False

        # 時間決済
        if self.is_time_exit(trade):
            result = True

        # 指定時刻決済
        elif self.is_close_time_exit(trade):
            result = True

        # 初期STOP待機
        elif self.is_initial_stop_delay(trade):
            result = False

        # STOP判定
        else:
            result = self.is_stop_hit(trade, price)


        return result

    #
    # TRAILING初期化
    #
    def init_trailing(self, trade, price):
        super().init_trailing(trade, price)

        entry = trade.runtime.entry_price
        atr = trade.param.atr

        entry_stop = entry - atr * trade.param.stop_atr_multiplier
        price_stop = price - atr * trade.param.stop_atr_multiplier
        trade.runtime.stop_price = min(entry_stop, price_stop)

        trade.runtime.trailing_highest_price = entry
        trade.runtime.trailing_lowest_price = None


    #
    # 高値更新
    #
    def update_trailing_stop_price(self, trade, price):
        if (
            trade.runtime.trailing_highest_price is None
            or price > trade.runtime.trailing_highest_price
        ):
            trade.runtime.trailing_highest_price = price

            new_stop = trade.runtime.trailing_highest_price - trade.param.atr * trade.param.trail_atr_multiplier

            if new_stop > trade.runtime.stop_price:
                trade.runtime.stop_price = new_stop

                Log.trailing(trade.id, f"TRAILING UPDATE LONG price={price} stop={trade.runtime.stop_price}")
                trade.add_timeline(type="TRAILING", message=f"UPDATE stop={trade.runtime.stop_price}")


    #
    # STOP判定
    #
    def is_stop_hit(self, trade, price):
        if price <= trade.runtime.stop_price:
            Log.trailing(trade.id, f"STOP HIT LONG price={price}")
            trade.add_timeline(type="EXIT", message=f"STOP HIT price={price}")

            # EXIT実績
            trade.runtime.exit_execution_price = price
            trade.runtime.exit_price = price
            trade.runtime.exit_time = datetime.now()

            return True

        return False
