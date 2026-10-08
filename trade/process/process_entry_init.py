#
# trade/process/process_entry_init.py
#
# Entry Init Process
#
# 役割:
#   ・ENTRY開始時の戦略別初期化
#

from core.logger import Log

from trade.process.process_base import ProcessBase

from trade.entry.entry_standard.process_entry_standard_init import (
    ProcessEntryStandardInit,
)

class ProcessEntryInit(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessEntryInit")

        self.process_entry_standard_init = ProcessEntryStandardInit(
            context,
            market,
        )

    def process(self, trade):

        Log.flow(f"(#{trade.id}) ProcessEntryInit:process")

        if trade.param.strategy_type == "standard":
            result = self.process_entry_standard_init.process(trade)
        else:
            result = True

        self.notify(trade, "ENTRY INIT")

        return result