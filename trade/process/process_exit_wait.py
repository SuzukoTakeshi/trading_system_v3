#
# trade/process/process_exit_wait.py
#

from core.logger import Log

from trade.process.process_base import ProcessBase

from market.order_enums import OrderState

from core.exception import (
    OrderNotFoundError,
    DuplicateOrderError,
)


class ProcessExitWait(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessExitWait")


    #
    # EXIT注文約定待ち
    #
    # TradeState.EXIT_WAITで呼ばれる
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

            Log.debug(f"EXIT WAIT (#{trade.id}) order_id={order.id} state={order.state.name}")

            result, result_dto = self.market.get_order_result(order.order_no)

            if result:

                #
                # 注文結果をOrderへ設定
                #
                order.result = result_dto

                order.change_state(OrderState.FILLED)

                Log.event(
                    f"EXIT ORDER FILLED (#{trade.id}) "
                    f"id={order.id} "
                    f"{order.symbol} "
                    f"order_no={order.order_no} "
                    f"price={result_dto.price}"
                )

                trade.add_timeline(
                    type="EXIT",
                    message=f"FILLED id={order.id} order_no={order.order_no} price={result_dto.price}"
                )

                return True

        return False


    #
    # Tradeに紐づく未完了Order取得
    #
    def get_order(self, trade):

        order = None

        for o in self.context.cache.orders.values():

            if o.trade.id != trade.id:
                continue

            #
            # CLOSED済みOrderは除外
            #
            if o.state == OrderState.CLOSED:
                continue

            #
            # 2件以上存在したら異常
            #
            if order is not None:
                raise DuplicateOrderError(
                    message=f"MULTIPLE ORDER trade={trade.id}",
                    code="MULTIPLE_ORDER",
                )

            order = o

        return order
