#
# trade/process/process_exit_wait.py
#

from core.logger import Log

from trade.process.process_base import ProcessBase

from market.order_enums import OrderState

from core.exception import (
    OrderNotFoundError,
    OrderDuplicateError,
    OrderMarketCancelError,
    OrderMarketNotFilledError,
)

from market.order_enums import OrderResultStatus


class ProcessExitWait(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessExitWait")


    # ==========================================
    # EXIT注文約定待ち
    #   TradeState.EXIT_WAITで呼ばれる
    # ==========================================
    def process(self, trade):

        Log.flow(f"(#{trade.id}) ProcessExitWait:process")

        order = self.get_order(trade)

        if order is None:
            raise OrderNotFoundError(
                message=f"(#{trade.id}) ORDER NOT FOUND",
                code="ORDER_NOT_FOUND",
            )

        # 注文受付済み
        if order.state == OrderState.REQUESTED:
            Log.trace("EXIT_WAIT", f"(#{trade.id}) (@{order.id}) EXIT WAIT state={order.state.name}")

            # 確認用：OrderListの生データを取得
            order.order_list_sheet_data = self.market.get_order_list_data(order.order_no)
            if order.order_list_sheet_data is None:
                return False

            # 注文結果取得　OrderResultModel
            result, order_result = self.market.get_order_result(order.order_no)

            if result:
                # 注文結果をOrderへ設定
                order.result = order_result

                order.change_state(OrderState.FILLED)

                text = (
                    f"(@{order.id}) EXIT ORDER FILLED symbol={order.symbol} "
                    f"order_no={order.order_no} price={order_result.price}"
                )
                Log.event(f"(#{trade.id}) {text}")
                trade.add_timeline(type="EXIT", message=text)

                return True

            if order_result.status in (
                OrderResultStatus.PARTIAL_FILLED,   # 一部約定
            ):
                return False

            if order_result.status in (
                OrderResultStatus.EXECUTION_WAIT,
                OrderResultStatus.EXECUTING,
            ):
                return False

            if order_result.status in (
                OrderResultStatus.CANCELING_FILLED,
                OrderResultStatus.CANCELING_UNFILLED,
                OrderResultStatus.CANCELED_FILLED,
                OrderResultStatus.CANCELED_UNFILLED,
            ):
                raise OrderMarketCancelError(
                    message=f"(#{trade.id}) CANCEL ORDER order_no={order.order_no}",
                    code="CANCEL_ORDER",
                )

            if order_result.status in (
                OrderResultStatus.NOT_FILLED_FILLED,
                OrderResultStatus.NOT_FILLED_UNFILLED,
            ):
                raise OrderMarketNotFilledError(
                    message=f"(#{trade.id}) NOT FILLED ORDER order_no={order.order_no}",
                    code="NOT_FILLED_ORDER",
                )

            if order_result.status in (     #訂正済
                OrderResultStatus.CORRECTED,
            ):
                return False

        return False


    # ==========================================
    # Tradeに紐づく未完了Order取得
    # ==========================================
    def get_order(self, trade):

        order = None
        for o in self.context.cache.orders.values():
            if o.trade.id != trade.id:
                continue

            # CLOSED済みOrderは除外
            if o.state == OrderState.CLOSED:
                continue

            # 2件以上存在したら異常
            if order is not None:
                raise OrderDuplicateError(
                    message=f"(#{trade.id}) MULTIPLE ORDER",
                    code="MULTIPLE_ORDER",
                )

            order = o

        return order
