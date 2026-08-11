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

        #
        # Trade chart data cache
        #
        # key:
        #   trade_id
        #
        # value:
        #   list[TradeChartData]
        #
        self.trade_chart_datas = {}



class EngineContext:

    def __init__(self):

        self.cycle_time = None

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
