#
# trade/trade_ready.py
#
# Trade Ready
#
# 役割:
#   ・Tradeを次の処理へ進めてよいか判定する
#   ・Tradeに必要な市場情報を取得する
#   ・市場情報をTradeパラメータへ反映する
#
# 判定:
#   True  = Trade処理可能
#   False = Trade処理待機
#
# debug:
#   市場時間やRSSのMarketDesに依存せず、
#   固定の市場情報を使用する。
#
# real / simulator:
#   MarketDesが取得できない場合はTradeを進めない。
#

class TradeReady:

    def __init__(self, market):
        self.market = market


    # ==========================================
    # Trade実行可否判定
    #
    # Return:
    #   True  = Trade処理可能
    #   False = Trade処理待機
    #
    # MarketDes:
    #   trading_unit
    #   lower_limit
    #   upper_limit
    #
    #   上記をTrade.paramへ設定する。
    # ==========================================
    def is_trade_ready(self, trade):

        symbol = trade.param.symbol

        #
        # Debug
        #
        # Debugでは実際のMarketDesを使用しない。
        # 市場時間やRSSの状態に関係なく、
        # Trade処理をテストできるよう固定値を使用する。
        #
        if self.market.mode == "debug":

            market_des = {
                "trading_unit": 100,
                "lower_limit": 1,
                "upper_limit": 999999,
            }

        #
        # Real / Simulator
        #
        # 実際のMarketDesを取得する。
        #
        # MarketDesが取得できない場合は、
        # 売買単位や制限値幅が不明なため、
        # Tradeを次の処理へ進めない。
        #
        else:

            market_des = self.market.get_market_des(symbol)

            if market_des is None:
                trade.message = "市場情報待ち"
                return False

        #
        # Tradeへ市場情報を反映
        #
        # この時点でMarketDesは取得済みなので、
        # Trade処理で利用できる状態になっている。
        #
        trade.param.trading_unit = market_des["trading_unit"]
        trade.param.lower_limit = market_des["lower_limit"]
        trade.param.upper_limit = market_des["upper_limit"]

        #
        # 待機メッセージをクリア
        #
        trade.message = ""

        return True