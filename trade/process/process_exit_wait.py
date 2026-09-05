#
# trade/process/process_exit_wait.py
#

from core.logger import Log

from trade.process.process_order_base import ProcessOrderBase


class ProcessExitWait(ProcessOrderBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessExitWait")


    def process(self, trade):
        """
        Order約定待ち

        TradeState.EXIT_WAITで呼ばれる
        """

        Log.flow(f"(#{trade.id}) ProcessExitWait:process")

        return self.order_result(trade)


    def on_order_filled(self, trade, order, order_result):
        """
        全量約定処理

        ProcessOrderBase:order_result()内より呼び出される。
        """

        trade.runtime.exit_price = order_result.price
        trade.runtime.exit_time = order_result.result_datetime

        message = (
            f"(@{order.id}) EXIT ORDER FILLED "
            f"symbol={order.symbol} "
            f"order_no={order.order_no} "
            f"quantity={order_result.quantity} "
            f"price={order_result.price}"
        )
        Log.event(f"(#{trade.id}) {message}")
        trade.add_timeline(event="EXIT", message=message)

        return True