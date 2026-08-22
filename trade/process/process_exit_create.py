#
# trade/process/process_exit_create.py
#

from datetime import datetime

from core.logger import Log

from trade.trade_enums import SideType

from market.order_enums import (
    OrderType,
    OrderAction,
    OrderState,
)

from trade.process.process_order_base import (
    ProcessOrderBase,
    ORDER_SUBMIT_TIMEOUT_SEC,
)

from core.exception import (
    InternalError,
    StrategySideDisabledError,
    OrderSubmitTimeoutError,
)


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

                    # 発注受付待ち開始時刻
                    # Orderのタイムアウトチェックの為、
                    # SUBMITTEDへ移行する直前に時刻を保存する。
                    order.submitted_at = datetime.now()

                    order.change_state(OrderState.SUBMITTED)

                case OrderState.SUBMITTED:

                    # 発注受付待ちタイムアウト
                    if order.submitted_at is None:
                        raise InternalError(
                            message=f"@({order.id}) Order submitted_at is None at ProcessExitCreate",
                            code="ORDER_SUBMIT_TIMESTAMP_MISSING",
                        )

                    elapsed = (datetime.now() - order.submitted_at).total_seconds()

                    if elapsed >= ORDER_SUBMIT_TIMEOUT_SEC:
                        raise OrderSubmitTimeoutError(
                            message=f"@({order.id}) Order submit timeout at ProcessExitCreate: elapsed={elapsed:.1f}s",
                            code="ORDER_SUBMIT_TIMEOUT",
                        )

                    order.order_no = self.get_order_no(trade, order)
                    if order.order_no is None:
                        return False

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
            trade.runtime.exit_price,
            OrderType.MARKET,       # 成行注文固定
            order_role="exit",
        )