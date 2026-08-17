#
# trade/process/process_exit_create.py
#

from core.logger import Log

from trade.trade_enums import SideType

from market.order_enums import (
    OrderType,
    OrderAction,
    OrderState,
)

from core.exception import StrategySideDisabledError

from trade.process.process_order_base import ProcessOrderBase


class ProcessExitCreate(ProcessOrderBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessExitCreate")


    def process(self, trade):

        order = self.find_order(trade)

        if order is None:
            order = self.create_exit_order(trade)

            order.change_state(OrderState.CREATED)

            return False

        else:
            match order.state:
                case OrderState.CREATED:
                    result = self.request_order(trade, order)
                    if not result:
                        return False

                    order.change_state(OrderState.SUBMITTED)

                case OrderState.SUBMITTED:
                    order.order_no = self.market.get_order_no(order.id)

                    order.change_state(OrderState.REQUESTED)

                    # True の後は呼ばれない
                    return True

                case _:
                    raise Exception(f"UNKNOWN ORDER STATE {order.state}")

        return False


    #
    # Exit Order生成
    #
    def create_exit_order(self, trade):
        if trade.param.side == SideType.LONG:
            order_action = OrderAction.SELL

        elif trade.param.side == SideType.SHORT:
            order_action = OrderAction.BUY

        else:
            raise StrategySideDisabledError(
                message=f"UNKNOWN SIDE {trade.param.side}",
                code="UNKNOWN_SIDE",
            )

        return self.create_order(
            trade,
            order_action,
            # 成行(OrderType.MARKET)だが、DEBUGで約定単価とする為、priceを渡している。
            trade.runtime.exit_execution_price,
            OrderType.MARKET,       # 成行注文固定
            order_role="exit",
        )