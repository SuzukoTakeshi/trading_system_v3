#
# trade/process/process_trailing_short.py
#
# Trailing Process Short
#
# 役割:
#   ・保有後のEXIT管理
#   ・初期STOP設定
#   ・STOP更新
#   ・損切り/利確判定
#

from core.logger import Log

from trade.process.process_trailing_base import ProcessTrailingBase


class ProcessTrailingShort(ProcessTrailingBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.debug("CREATE ProcessTrailingShort")


    #
    # TradeState.TRAILINGで呼ばれる
    #
    def process(self, trade):
        if super().process(trade) == False:
            return False

        price = self.price

        # 初回TRAILING初期化
        if trade.runtime.stop_price is None:
            self.init_trailing(trade, price)

        Log.debug(
            f"TRAILING CHECK id={trade.id} price={price} "
            f"highest={trade.runtime.trailing_highest_price} stop={trade.runtime.stop_price}"
        )

        #
        # トレーリング更新
        #
        self.update_trailing_stop_price(trade, price)

        #
        # 時間決済
        #
        if self.is_time_exit(trade):
            Log.event(f"TIME EXIT id={trade.id}")
            trade.add_timeline(type="EXIT", message=f"TIME EXIT limit={trade.param.time_limit_minutes}min")
            return True

        #
        # 初期STOP待機
        #
        if self.is_initial_stop_delay(trade):
            return False

        #
        # STOP判定
        #
        return self.is_stop_hit(trade, price)


    #
    # TRAILING初期化
    #
    def init_trailing(self, trade, price):
        super().init_trailing(trade, price)

        entry = trade.runtime.entry_price
        atr = trade.param.atr

        entry_stop = entry + atr * trade.param.stop_atr_multiplier
        price_stop = price + atr * trade.param.stop_atr_multiplier
        trade.runtime.stop_price = max(entry_stop, price_stop)

        trade.runtime.trailing_lowest_price = entry
        trade.runtime.trailing_highest_price = None


    #
    # 安値更新
    #
    def update_trailing_stop_price(self, trade, price):
            if (
                trade.runtime.trailing_lowest_price is None
                or price < trade.runtime.trailing_lowest_price
            ):
                trade.runtime.trailing_lowest_price = price

                new_stop = (
                    trade.runtime.trailing_lowest_price + trade.param.atr * trade.param.trail_atr_multiplier
                )

                if new_stop < trade.runtime.stop_price:
                    trade.runtime.stop_price = new_stop

                    Log.event(f"TRAILING UPDATE SHORT id={trade.id} price={price} stop={trade.runtime.stop_price}")
                    trade.add_timeline(type="TRAILING", message=f"UPDATE stop={trade.runtime.stop_price}")


    #
    # STOP判定
    #
    def is_stop_hit(self, trade, price):
        if price >= trade.runtime.stop_price:
            Log.event(f"STOP HIT SHORT id={trade.id} price={price}")
            trade.add_timeline(type="EXIT", message=f"STOP HIT price={price}")
            return True

        return False
