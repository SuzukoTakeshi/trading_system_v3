#
# trade/process/process_base.py
#

class ProcessBase:

    def __init__(self, context, market):

        # 共通データ
        self.context = context

        # 市場サービス
        self.market = market
