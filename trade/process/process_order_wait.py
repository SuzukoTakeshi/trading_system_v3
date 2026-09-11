#
# trade/process/process_order_wait.py
#

from core.logger import Log

from trade.process.process_order_base import ProcessOrderBase


class ProcessOrderWait(ProcessOrderBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessOrderWait")


    def process(self, trade):
        """
        Order約定待ち TradeState.ORDER_WAITで呼ばれる
        """

        Log.flow(f"(#{trade.id}) ProcessOrderWait:process")

        return self.order_result(trade, trade.entry_order)


    def on_order_filled(self, trade, order, order_result):
        """
        全量約定処理 ProcessOrderBase:order_result()内より呼び出される。
        """

        trade.runtime.entry_price = order_result.price

        message = (
            f"(@{order.id}) ORDER FILLED "
            f"order_no={order.order_no} "
            f"symbol={order.symbol} "
            f"quantity={order_result.quantity} "
            f"price={order_result.price} "
            f"result_datetime={order_result.result_datetime} "
            f"market_name={order_result.market_name}"
        )
        Log.event(f"(#{trade.id}) {message}")
        trade.add_timeline(event="ORDER", message=message)

        return True