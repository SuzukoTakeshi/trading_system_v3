#
# trade/cycle/order_proc.py
#
# Order Cycle Process
#
# 役割:
#   ・Order監視
#   ・発注処理
#   ・Order状態更新
#
#

from core.logger import Log

from trade.enums import OrderState

from market.dto import (
	OrderRequestDTO,
	GetOrderNoRequestDTO,
)


class OrderProc:

    def __init__(self, context, market):

        # 共通データ
        self.context = context

        # Market Service
        self.market = market


    def process(self, order):
        """
        1 Order処理
        """

        Log.debug(f"ORDER PROC {order.id} state={order.state}")

        if order.state == OrderState.REQUEST:
            if self._request_order(order):
                order.change_state(OrderState.SUBMITTED)
            else:
                Log.error(f"ORDER REQUEST FAILED order={order.id}")

        if order.state == OrderState.SUBMITTED:
            if self._get_order_no(order):
                order.change_state(OrderState.REQUESTED)
            else:
                Log.error(f"GET ORDER NO FAILED order={order.id}")

        if order.state == OrderState.REQUESTED:
            #約定確認
            if self.market.get_order_result(order):
                order.change_state(OrderState.FILLED)


    def _request_order(self, order):
        """
        発注処理
        """

        request = OrderRequestDTO(
            order_id=order.id,
            symbol=order.symbol,
            order_action=order.order_action,
            quantity=order.quantity,
            price=order.price,
        )

        result = self.market.request_order(request)

        Log.debug(f"REQUEST ORDER {order.id} {order.symbol}: result={result}")

        return result

    # 注文番号取得
    #
    def _get_order_no(self, order):

        request = GetOrderNoRequestDTO(order_id=order.id, symbol=order.symbol)
        result, order_no = self.market.get_order_no(request)
        if not result:
            return False

        order.order_no = order_no

        return True
