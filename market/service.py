#
# market/service.py
#
# Market Service
#
# 役割:
#   ・Market機能の窓口
#   ・TradeEngineから利用される
#

from core.logger import Log

from market.order_enums import OrderResultStatus
from market.rakuten.market import RakutenMarket

from models.order.order_result_model import OrderResultModel


class MarketService:

    def __init__(self, mode):
        self.mode = mode

        # Market
        self.market = RakutenMarket(self.mode)

    # ==========================================
    # Market開始
    # ==========================================
    def open(self):
        Log.debug("MARKET OPEN")
        self.market.open()


    # ==========================================
    # Market終了
    # ==========================================
    def close(self):
        Log.debug("MARKET CLOSE")
        self.market.close()


    def sync_market(self, symbols):
        self.market.sync_quotes(symbols)


    def get_quote(self, symbol):
        return self.market.get_quote(symbol)


    def get_market_des(self, symbol):
        return self.market.get_market_des(symbol)


    def remove_quote_symbol(self, symbol):
        self.market.remove_quote_symbol(symbol)


    # ==========================================
    # 発注依頼
    #   ・Marketへ注文を依頼する
    #   ・Trade層とはDTOで分離
    # ==========================================
    def request_order(self, request_dto):
         return self.market.request_order(request_dto)


    # ==========================================
    # 発注ID一覧データ取得
    #   ・Marketから発注ID一覧シートの1行分データを取得する
    #   ・Trade層とはデータで分離
    # ==========================================
    def get_order_id_data(self, order_id):
        return self.market.get_order_id_data(order_id)


    # ==========================================
    # 注文一覧データ取得
    #   ・Marketから注文一覧シートの1行分の生データを取得する
    #   ・Trade層とはデータで分離
    # ==========================================
    def get_order_list_data(self, order_no):
        return self.market.get_order_list_data(order_no)


    # ==========================================
    # 注文番号取得
    #   ・Marketから注文番号を取得する
    #   ・Trade層とはDTOで分離
    # ==========================================
    def get_order_no(self, order_id):
        return self.market.get_order_no(order_id)


    # ==========================================
    # 注文結果取得
    # ==========================================
    def get_order_result(self, order_no):

        data = self.market.get_order_result(order_no)
        if data is None:
            raise Exception(f"[@({order_no}) ORDER RESULT NOT FOUND")

        order_result = OrderResultModel(
            order_no=data["order_no"],
            status=OrderResultStatus(data["status"]),
            order_datetime=data["order_datetime"],
            quantity=data["quantity"],
            price=data["price"],
        )

        if order_result.status == OrderResultStatus.FILLED:
            return True, order_result

        else:
            return False, order_result