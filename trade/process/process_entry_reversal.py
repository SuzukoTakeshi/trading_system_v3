#
# trade/process/process_entry_reversal.py
#

from core.logger import Log

from trade.trade_enums import SideType

from trade.process.process_base import ProcessBase

from trade.process.process_entry_reversal_long import ProcessEntryReversalLong
from trade.process.process_entry_reversal_short import ProcessEntryReversalShort

from core.exception import StrategySideDisabledError


class ProcessEntryReversal(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        self.long = ProcessEntryReversalLong(
            context,
            market
        )

        self.short = ProcessEntryReversalShort(
            context,
            market
        )

        Log.debug("CREATE ProcessEntryReversal")

    def process(self, trade):

        quote = self.context.cache.quotes.get(
            trade.param.symbol
        )

        if quote is None:
            return False

        if trade.param.side == SideType.LONG:
            return self.long.process(trade, quote)

        elif trade.param.side == SideType.SHORT:
            return self.short.process(trade, quote)

        else:
            raise StrategySideDisabledError(
                message=f"UNKNOWN SIDE {trade.param.side}",
                code="UNKNOWN_SIDE",
            )
