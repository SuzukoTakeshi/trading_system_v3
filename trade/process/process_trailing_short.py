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

    def process(self, trade):

        # message = (
        #     f"TRAILING CHECK SHORT price={trade.runtime.quote.current_price} "
        #     f"lowest={trade.runtime.trailing_lowest_price} stop={trade.runtime.stop_price}"
        # )
        # Log.event(f"(#{trade.id}) {message}")

        return super().process(trade)


    # ==========================================
    # TRAILING初期化
    #   ProcessTrailingBaseからの呼び出し
    # ==========================================
    def init_trailing(self, trade):
        super().init_trailing(trade)

        entry = trade.runtime.entry_price
        atr = trade.param.atr

        # ENTRYでの約定価格から初期STOP価格を設定する
        trade.runtime.stop_price = (
            entry + atr * trade.param.stop_atr_multiplier
        )

        trade.runtime.trailing_lowest_price = entry
        trade.runtime.trailing_highest_price = None

        # 通知
        self.notify(trade, "INIT TRAILING SHORT")


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

            message = (f"TRAILING LOW UPDATE SHORT current_price={current_price}")
            Log.event(f"(#{trade.id}) {message}")
            trade.add_timeline(event="TRAILING", message=message, current_price=current_price)

            new_stop = trade.runtime.trailing_lowest_price + trade.param.atr * trade.param.trail_atr_multiplier

            if new_stop < trade.runtime.stop_price:
                trade.runtime.stop_price = new_stop

                message = f"TRAILING UPDATE SHORT current_price={current_price} stop={trade.runtime.stop_price}"
                Log.event(f"(#{trade.id}) {message}")
                trade.add_timeline(event="TRAILING", message=message, current_price=current_price)


    # ==========================================
    # 損切ライン(STOP)判定
    # ==========================================
    def is_stop_hit(self, trade):

        current_price = self.quote.current_price

        if current_price >= trade.runtime.stop_price:
            message = f"STOP HIT SHORT current_price={current_price} >= stop_price={trade.runtime.stop_price}"
            Log.event(f"(#{trade.id}) {message}")
            trade.add_timeline(event="EXIT", message=message, current_price=current_price)

            trade.runtime.set_exit(current_price, ExitReason.STOP_LINE_EXIT)

            return True

        return False
