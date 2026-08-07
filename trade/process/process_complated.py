#
# trade/process/process_complated.py
#

from core.logger import Log

from trade.process.process_base import ProcessBase


class ProcessComplated(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.debug("CREATE ProcessComplated")

    def process(self, trade):

        return True
