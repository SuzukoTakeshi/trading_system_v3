#
# trade/cycle/strategy_proc_short.py
#
# Strategy Process Short
#
# 役割:
#   ・売買判断
#   ・ENTRY判定
#   ・戦略パラメータ更新
#
#

from core.logger import Log

from trade.enums import (
    TradeState,
    EntryState,
    OrderAction,
)

from trade.cycle.strategy_proc_base import StrategyProcBase


class StrategyProcShort(StrategyProcBase):

    def __init__(self, context, market):
        super().__init__(context, market)


    def process(self, trade):
        super().process(trade)

        self.debug_print_price()

        # ENTRY待機
        if trade.state == TradeState.WAITING:
            self.check_entry()

        # 注文中
        elif trade.state == TradeState.ACTIVE:
            pass

        # 保有中
        elif trade.state == TradeState.HOLDING:

            self.initialize_stop_price()

            self.update_stop_price()

            self.check_stop_loss()


    # ==================================================
    # SHORT ENTRY判定
    #
    # 上昇確認
    # ↓
    # 反転確認
    #
    # ==================================================
    #
    def check_entry(self):
        super().check_entry()

        trade = self.trade 
        price = self.quote.price

        cfg = self.get_entry_config()

        # 戻り幅
        pullback_width = trade.atr * cfg["pullback_atr_multiplier"]

        # 上昇ライン
        pushup_price = trade.price + pullback_width

        # 初期状態
        if trade.entry_state == EntryState.WAITING:
            if price >= pushup_price:
                trade.entry_state = (EntryState.PULLBACK)
                trade.entry_highest_price = price
                trade.entry_previous_price = price
                trade.entry_reversal_count = 0

                Log.event(f"ENTRY PUSHUP {trade.symbol} {price}")
            return


        if trade.entry_state in (EntryState.PULLBACK, EntryState.REVERSAL):

            # 高値更新
            if (
                trade.entry_highest_price is None
                or
                price > trade.entry_highest_price
            ):
                trade.entry_highest_price = price
                trade.entry_reversal_count = 0

            # 下落確認
            if (
                trade.entry_previous_price is not None
                and
                price < trade.entry_previous_price
            ):
                trade.entry_reversal_count += 1

            trade.entry_previous_price = price

            # 反転確認
            if (
                trade.entry_reversal_count
                >=
                cfg["reversal_confirm_count"]
            ):
                trade.entry_state = (EntryState.REVERSAL)
                super().create_order(OrderAction.SELL)
                trade.change_state(TradeState.ACTIVE)


    # ==================================================
    # SHORT 初期STOP設定
    #
    # 約定後、最初の損切りラインを設定する
    #
    # ==================================================
    #
    def initialize_stop_price(self):

        trade = self.trade

        if trade.stop_price is not None:
            return

        if trade.entry_price is None:
            return

        multiplier = (
            self.config.data
            ["atr_stop_multiplier"]
        )

        trade.stop_price = (
            trade.entry_price
            +
            trade.atr * multiplier
        )

        Log.event(
            f"INIT STOP SHORT "
            f"{trade.symbol} {trade.stop_price}"
        )


    # ==================================================
    # SHORT STOP更新
    #
    # ブレークイーブン
    #
    # ==================================================
    #
    def update_stop_price(self):

        trade = self.trade
        price = self.quote.price

        if trade.entry_price is None:
            return

        if trade.stop_price is None:
            return


        cfg = (
            self.config.data
            ["breakeven"]
        )


        if not cfg["enabled"]:
            return


        profit_rate = (
            trade.entry_price
            -
            price
        ) / trade.entry_price


        if profit_rate >= cfg["trigger"]:

            if trade.stop_price > trade.entry_price:

                trade.stop_price = trade.entry_price

                Log.event(
                    f"BREAKEVEN SHORT "
                    f"{trade.symbol} "
                    f"stop={trade.stop_price}"
                )


    def check_stop_loss(self):
        super().check_stop_loss()

        trade = self.trade
        price = self.quote.price

        if trade.stop_price is None:
            return

        Log.debug(
            f"STOP CHECK SHORT "
            f"{trade.symbol} "
            f"price={price} "
            f"stop={trade.stop_price}"
        )

        if price >= trade.stop_price:

            Log.event(
                f"STOP LOSS SHORT "
                f"{trade.symbol} "
                f"{price} >= {trade.stop_price}"
            )

            self.close_trade_orders(trade)

            super().create_order(OrderAction.BUY)

            trade.change_state(TradeState.EXITING)
