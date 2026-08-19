#
# trade/process/process_order_wait.py
#

from datetime import datetime

from core.logger import Log

from trade.process.process_base import ProcessBase

from market.order_enums import OrderState

from core.exception import (
	OrderNotFoundError,
	DuplicateOrderError,
    CancelOrderResult,
    NotFilledOrderResult,
)

from market.order_enums import OrderResultStatus


class ProcessOrderWait(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessOrderWait")


    #
    # Order約定待ち
    #
    # TradeState.ORDER_WAITで呼ばれる
    #
    def process(self, trade):

        order = self.get_order(trade)

        if order is None:
            raise OrderNotFoundError(
                message=f"ORDER NOT FOUND (#{trade.id})",
                code="ORDER_NOT_FOUND",
            )


        #
        # 注文受付済み
        #
        if order.state == OrderState.REQUESTED:
            Log.trace("ORDER_WAIT", f"(#{trade.id}) order_id={order.id} state={order.state.name}")

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

                trade.runtime.entry_price = order_result.price
                trade.runtime.entry_time = datetime.now()

                Log.event(
                    f"ORDER FILLED (#{trade.id}) (@{order.id}) symbol={order.symbol} "
                    f"order_no={order.order_no} price={order_result.price}"
                )

                trade.add_timeline(
                    type="ORDER",
                    message=f"FILLED id={order.id} order_no={order.order_no} price={order_result.price}",
                )

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
                raise CancelOrderResult(
                    message=f"CANCEL ORDER (#{trade.id}) @({order.order_no}) ",
                    code="CANCEL_ORDER",
                )

            if order_result.status in (
                OrderResultStatus.NOT_FILLED_FILLED,
                OrderResultStatus.NOT_FILLED_UNFILLED,
            ):
                raise NotFilledOrderResult(
                    message=f"NOT FILLED ORDER (#{trade.id}) @({order.order_no})",
                    code="NOT_FILLED_ORDER",
                )

            if order_result.status in (     #訂正済
                OrderResultStatus.CORRECTED,
            ):
                return False

        return False


    #
    # Tradeに紐づくOrder取得
    #
    def get_order(self, trade):
        order = None
        for o in self.context.cache.orders.values():
            if o.trade.id == trade.id:
                if order:
                    raise DuplicateOrderError(
                        message=f"MULTIPLE ORDER trade={trade.id}",
                        code="MULTIPLE_ORDER",
                    )
                order = o
                
        return order