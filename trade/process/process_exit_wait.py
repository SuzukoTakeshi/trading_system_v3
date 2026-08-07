#
# trade/process/process_exit_wait.py
#

from core.logger import Log

from trade.process.process_base import ProcessBase


class ProcessExitWait(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.debug("CREATE ProcessExitWait")

    def process(self, trade):

        return True
