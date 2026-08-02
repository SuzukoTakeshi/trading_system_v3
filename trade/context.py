#
# trade/context.py
#
# Trade Engine Context
#
# 役割:
#   ・Engine共通データ管理
#   ・Cycle間データ共有
#
#

class EngineCache:

    def __init__(self):

        #
        # Quote cache
        #
        # key:
        #   symbol
        #
        # value:
        #   QuoteModel
        #
        self.quotes = {}


        #
        # Order cache
        #
        # key:
        #   trade_id
        #
        # value:
        #   Order
        #
        self.orders = {}



class EngineContext:

    def __init__(self):

        #
        # 管理中Trade
        #
        # key:
        #   trade_id
        #
        # value:
        #   TradeModel
        #
        self.trades = {}


        #
        # Cycle共有データ
        #
        self.cache = EngineCache()