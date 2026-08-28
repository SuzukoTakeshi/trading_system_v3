#
# trade/process/process_market.py
#
# Market Process
#
# 役割:
#   ・Trade作成直後のMarket処理枠
#
# 現在:
#   ・Quote取得はTradeReadyが担当
#   ・QuoteModel生成/更新もTradeReadyが担当
#   ・そのため現在の処理はない
#
# 将来:
#   ・Market関連の初期処理が必要になった場合に使用する。
#

from core.logger import Log

from trade.process.process_base import ProcessBase


class ProcessMarket(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("MarketProc")


    def process(self, trade):

        return True