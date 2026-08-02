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

from market.rakuten.client import RakutenClient

from models.order.order_result_model import OrderResultModel

class MarketService:

    def __init__(self):

        # Client
        self.client = RakutenClient()


    def open(self):
        """
        Market開始

        ・楽天RSS Excel接続
        ・Market利用準備
        """

        Log.event("MARKET OPEN")

        self.client.open()


    def close(self):
        """
        Market終了

        ・楽天RSS Excel切断
        """

        Log.event("MARKET CLOSE")

        self.client.close()


    def sync_market(self, symbols):
        self.client.sync_quotes(symbols)
        return self.client.get_quotes()


    def get_quote(self, symbol):
        return self.client.get_quote(symbol)


    def get_quotes(self):
        """
        現在の市場情報取得

        ・監視銘柄の現在値取得
        ・Quotesシートの内容を読み込む
        """

        return self.client.get_quotes()


    def request_order(self, request):
        """
        発注依頼

        ・Marketへ注文を依頼する
        ・Trade層とはDTOで分離
        """

        return self.client.request_order(request)


    def get_order_no(self, request):
        """
        注文番号取得

        ・Marketから注文番号を取得する
        ・Trade層とはDTOで分離
        """

        return self.client.get_order_no(request)


    def get_order_result(self, order):
        """
        注文結果取得
        """

        data = self.client.get_order_result(order.order_no)
        if data is None:
            raise Exception(
                f"ORDER RESULT NOT FOUND order_no={order.order_no}"
            )

        order.order_result = OrderResultModel(
            order_no=data["order_no"],
            status=data["status"],
            order_datetime=data["order_datetime"],
            quantity=data["quantity"],
            price=data["price"],
        )

        if order.order_result.status == "約定":
            return True

        else:
            return False