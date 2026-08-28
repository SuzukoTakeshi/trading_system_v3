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

from trade.trade_enums import ExitReason


class ProcessTrailingShort(ProcessTrailingBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessTrailingShort")

    # ==========================================
    # TradeState.TRAILINGで呼ばれる
    # ==========================================
    def process(self, trade):
        if super().process(trade) == False:
            return False

        current_price = self.quote.current_price

        Log.trailing(trade.id,
            f"TRAILING CHECK price={current_price} "
            f"lowest={trade.runtime.trailing_lowest_price} stop={trade.runtime.stop_price}"
        )

        # トレーリング更新
        self.update_trailing_stop_price(trade)

        result = False

        # 1日信用 強制手仕舞い (ProcessTrailingBase)
        if self.is_margin_day_close(trade):
            result = True

        # 時間決済 (ProcessTrailingBase)
        elif self.is_time_exit(trade):
            result = True

        # 指定時刻決済 (ProcessTrailingBase)
        elif self.is_close_time_exit(trade):
            result = True

        # 初期STOP待機 (ProcessTrailingBase)
        elif self.is_initial_stop_delay(trade):
            result = False

        # STOP判定
        else:
            result = self.is_stop_hit(trade)

        return result


    # ==========================================
    # TRAILING初期化
    #   ProcessTrailingBaseからの呼び出し
    # ==========================================
    def init_trailing(self, trade):
        super().init_trailing(trade)

        current_price = self.quote.current_price

        entry = trade.runtime.entry_price
        atr = trade.param.atr

        entry_stop = entry + atr * trade.param.stop_atr_multiplier
        price_stop = current_price + atr * trade.param.stop_atr_multiplier
        trade.runtime.stop_price = max(entry_stop, price_stop)

        trade.runtime.trailing_lowest_price = entry
        trade.runtime.trailing_highest_price = None


    # ==========================================
    # 安値更新
    # ==========================================
    def update_trailing_stop_price(self, trade):

        current_price = self.quote.current_price

        if (
            trade.runtime.trailing_lowest_price is None
            or current_price < trade.runtime.trailing_lowest_price
        ):
            trade.runtime.trailing_lowest_price = current_price

            new_stop = trade.runtime.trailing_lowest_price + trade.param.atr * trade.param.trail_atr_multiplier

            if new_stop < trade.runtime.stop_price:
                trade.runtime.stop_price = new_stop

                Log.trailing(trade.id, f"TRAILING UPDATE SHORT current_price={current_price} stop={trade.runtime.stop_price}")
                trade.add_timeline(type="TRAILING", message=f"UPDATE stop={trade.runtime.stop_price}")


    # ==========================================
    # STOP判定
    # ==========================================
    def is_stop_hit(self, trade):

        current_price = self.quote.current_price

        if current_price >= trade.runtime.stop_price:
            message = f"STOP HIT SHORT current_price={current_price}"
            Log.trailing(trade.id, message)
            trade.add_timeline(type="EXIT", message=message)

            trade.runtime.set_exit(current_price, ExitReason.STOP)

            return True

        return False
