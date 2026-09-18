#
# trade/process/process_completed.py
#

from core.logger import Log

from trade.trade_enums import SideType

from trade.process.process_base import ProcessBase


class ProcessCompleted(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessCompleted")

    def process(self, trade):

        Log.flow(f"(#{trade.id}) ProcessCompleted:process")

        entry_result = trade.entry_order.result
        exit_result = trade.exit_order.result

        if trade.param.side == SideType.LONG:
            profit_loss = (exit_result.price - entry_result.price) * trade.param.quantity
            notify_id = "COMPLETED LONG " + ("PROFIT" if profit_loss >= 0 else "LOSS")

        elif trade.param.side == SideType.SHORT:
            profit_loss = (entry_result.price - exit_result.price) * trade.param.quantity
            notify_id = "COMPLETED SHORT " + ("PROFIT" if profit_loss < 0 else "LOSS")

        self.notify(trade, notify_id)

        return True
