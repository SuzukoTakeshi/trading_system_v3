#
# trade/process/process_base.py
#

from core.logger import Log


class ProcessBase:

    def __init__(self, context, market):

        # 共通データ
        self.context = context

        # 市場サービス
        self.market = market


    def notify(self, trade, notify_id):
        self.context.notifier_trade.notify(trade, notify_id)
