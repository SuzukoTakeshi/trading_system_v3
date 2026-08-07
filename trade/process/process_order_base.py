#
# trade/process/process_order_base.py
#
# Order Process Base
#
# 役割:
#   ・Order処理共通
#   ・Order検索
#   ・Order生成
#   ・発注処理
#

from core.logger import Log

from trade.process.process_base import ProcessBase

from trade.order_enums import (
	OrderType,
	OrderState,
)

from models.order.order_model import OrderModel

from market.dto import OrderRequestDTO

from core.exception import DuplicateOrderError


class ProcessOrderBase(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

    # Tradeに紐づくOrder取得
    def find_order(self, trade):

        order = None

        for o in self.context.cache.orders.values():
            if o.trade.id != trade.id:
                continue

            # 処理対象Order
            if o.state in (OrderState.CREATED, OrderState.SUBMITTED):
                if order:
                    raise DuplicateOrderError(
                        message=f"MULTIPLE ACTIVE ORDER trade={trade.id}",
                        code="MULTIPLE_ACTIVE_ORDER",
                    )
                order = o

        return order


    #
    # Order生成
    #
    def create_order(self, trade, order_action, price, order_type=OrderType.MARKET):

        order = OrderModel(
            trade=trade,
            symbol=trade.param.symbol,
            order_action=order_action,
            price=price,
            quantity=trade.param.quantity,
            order_type=order_type,
        )

        self.context.cache.orders[order.id] = order

        Log.event(
            f"CREATE ORDER "
            f"{order.id} "
            f"trade={trade.id} "
            f"{trade.param.symbol} "
            f"{order_action.value}"
        )

        trade.add_timeline(
            type="ORDER",
            message=(
                f"CREATE id={order.id} "
                f"order_action={order.order_action.value} "
                f"price={order.price} "
                f"quantity={order.quantity} "
                f"order_type={order.order_type.value}"
            )
        )

        return order


    #
    # 発注処理
    #
    def request_order(self, trade, order):
        request = OrderRequestDTO(
            order_id=order.id,
            symbol=order.symbol,
            order_action=order.order_action,
            quantity=order.quantity,
            price=order.price,
            order_type=order.order_type,
        )

        result = self.market.request_order(request)

        Log.event(f"REQUEST ORDER {order.id} {order.symbol} result={result}")

        trade.add_timeline(
            type="ORDER",
            message=f"REQUEST id={order.id} result={result}"
        )

        if not result:
            order.change_state(OrderState.ERROR)

            raise Exception(f"ORDER REQUEST FAILED order={order.id}")

        return result