#
# trade/process/process_order_wait.py
#

from datetime import datetime

from core.logger import Log

from trade.process.process_base import ProcessBase

from trade.order_enums import OrderState

from core.exception import (
	OrderNotFoundError,
	DuplicateOrderError,
)


class ProcessOrderWait(ProcessBase):

    def __init__(self, context, market):

        super().__init__(
            context,
            market
        )

        Log.debug("CREATE ProcessOrderWait")


    #
    # Order約定待ち
    #
    # TradeState.ORDER_WAITで呼ばれる
    #
    def process(self, trade):

        order = self.get_order(trade)

        if order is None:
            raise OrderNotFoundError(
                message=(
                    f"ORDER NOT FOUND "
                    f"trade={trade.id}"
                ),
                code="ORDER_NOT_FOUND",
            )


        #
        # 注文受付済み
        #
        if order.state == OrderState.REQUESTED:
            Log.debug(
                f"ORDER WAIT "
                f"order_id={order.id} "
                f"state={order.state.name}"
            )

            result, result_dto = self.market.get_order_result(order.order_no)

            if result:
                order.filled_price = result_dto.price

                order.change_state(OrderState.FILLED)

                trade.runtime.entry_price = result_dto.price
                trade.runtime.entry_time = datetime.now()

                Log.event(
                    f"ORDER FILLED "
                    f"id={order.id} "
                    f"trade={trade.id} "
                    f"{order.symbol} "
                    f"order_no={order.order_no} "
                    f"price={order.filled_price}"
                )

                trade.add_timeline(
                    type="ORDER",
                    message=(
                        f"FILLED id={order.id} "
                        f"order_no={order.order_no} "
                        f"price={order.filled_price}"
                    )
                )

                return True


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
                        message=(
                            f"MULTIPLE ORDER "
                            f"trade={trade.id}"
                        ),
                        code="MULTIPLE_ORDER",
                    )

                order = o

        return order