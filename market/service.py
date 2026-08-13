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
from market.rakuten.client import RakutenClient

from models.order.order_result_model import OrderResultModel


class MarketService:

    def __init__(self, mode):
        self.mode = mode

        # Client
        self.client = RakutenClient(self.mode)


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


    def get_quote(self, symbol):
        return self.client.get_quote(symbol)


    def request_order(self, request_dto):
        """
        発注依頼

        ・Marketへ注文を依頼する
        ・Trade層とはDTOで分離
        """

        return self.client.request_order(request_dto)


    def get_order_no(self, order_id):
        """
        注文番号取得

        ・Marketから注文番号を取得する
        ・Trade層とはDTOで分離
        """

        return self.client.get_order_no(order_id)


    def get_order_result(self, order_no):
        """
        注文結果取得
        """

        data = self.client.get_order_result(order_no)
        if data is None:
            raise Exception(
                f"ORDER RESULT NOT FOUND order_no={order_no}"
            )

        order_result = OrderResultModel(
            order_no=data["order_no"],
            status=OrderResultStatus(
                data["status"]
            ),
            order_datetime=data["order_datetime"],
            quantity=data["quantity"],
            price=data["price"],
        )

        if order_result.status == OrderResultStatus.FILLED:
            return True, order_result

        else:
            return False, order_result