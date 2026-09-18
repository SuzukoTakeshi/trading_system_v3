#
# trade/process/process_exit_result.py
#

from core.logger import Log

from trade.process.process_order_base import ProcessOrderBase


class ProcessExitResult(ProcessOrderBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessExitResult")


    def process(self, trade):
        """
        Order約定待ち

        TradeState.EXIT_RESULTで呼ばれる
        """

        Log.flow(f"(#{trade.id}) ProcessExitResult:process")

        return self.order_result(trade, trade.exit_order)


    def on_order_filled(self, trade, order, order_result):
        """
        全量約定処理

        ProcessOrderBase:order_result()内より呼び出される。
        """

        message = (
            f"(@{order.id}) EXIT ORDER FILLED "
            f"symbol={order.symbol} "
            f"order_no={order.order_no} "
            f"quantity={order_result.quantity} "
            f"price={order_result.price} "
            f"result_datetime={order_result.result_datetime} "
            f"market_name={order_result.market_name}"
        )
        Log.event(f"(#{trade.id}) {message}")
        trade.add_timeline(event="EXIT", message=message)

        return True
