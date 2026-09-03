#
# trade/process/process_complated.py
#

from core.logger import Log

from trade.trade_enums import SideType

from trade.process.process_base import ProcessBase



class ProcessComplated(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessComplated")

    def process(self, trade):

        Log.flow(f"(#{trade.id}) ProcessComplated:process")

        profit_loss = (trade.runtime.exit_price - trade.runtime.entry_price) * trade.param.quantity

        if trade.param.side == SideType.LONG:
            notify_id = "COMPLETED LONG " + ("PROFIT" if profit_loss >= 0 else "LOSS")

        elif trade.param.side == SideType.SHORT:
            notify_id = "COMPLETED SHORT " + ("PROFIT" if profit_loss < 0 else "LOSS")

        self.notify(trade, notify_id)

        return True
