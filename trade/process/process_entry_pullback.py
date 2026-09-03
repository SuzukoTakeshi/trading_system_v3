#
# trade/process/process_entry_pullback.py
#

from core.logger import Log

from trade.trade_enums import SideType

from trade.process.process_base import ProcessBase

from trade.process.process_entry_pullback_long import ProcessEntryPullbackLong
from trade.process.process_entry_pullback_short import ProcessEntryPullbackShort

from core.exception import InternalError


class ProcessEntryPullback(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessEntryPullback")

        self.long = ProcessEntryPullbackLong(context, market)
        self.short = ProcessEntryPullbackShort(context, market)


    def process(self, trade):

        quote = trade.runtime.quote

        if trade.param.side == SideType.LONG:
            return self.long.process(trade, quote)
        elif trade.param.side == SideType.SHORT:
            return self.short.process(trade, quote)
        else:
            raise InternalError(message=f"UNKNOWN SIDE {trade.param.side}", code="UNKNOWN_SIDE")
