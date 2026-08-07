#
# trade/process/process_canceled.py
#

from core.logger import Log

from trade.process.process_base import ProcessBase


class ProcessCanceled(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.debug("CREATE ProcessCanceled")

    def process(self, trade):

        return True
