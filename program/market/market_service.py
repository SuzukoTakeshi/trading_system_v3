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

from market.status import MarketStatus

from market.rakuten.rakuten_client import RakutenClient

from core.exception import OrderResultError


class MarketService:

    def __init__(self, mode):
        self.mode = mode

        # RakutenClient
        self.rakuten_client = RakutenClient(self.mode)

        # Market Status
        self.market_status = MarketStatus(
            self.rakuten_client.get_market_session()
        )

    def is_real(self):
        return self.mode == "real"

    def is_simulator(self):
        return self.mode == "simulator"

    def is_emulator(self):
        return self.mode == "emulator"

    def is_debug(self):
        return self.mode == "debug"


    # ==========================================
    # 楽天CLIENT OPEN
    # ==========================================
    def open(self):
        Log.debug("RAKUTEN CLIENT OPEN")
        self.rakuten_client.open()


    # ==========================================
    # 楽天CLIENT CLOSE
    # ==========================================
    def close(self):
        Log.debug("RAKUTEN CLIENT CLOSE")
        self.rakuten_client.close()


    def get_status(self):
        return self.market_status.get()

    def get_session_event(self):
        return self.market_status.get_session_event()

    def sync_market(self, symbols):
        self.rakuten_client.sync_quotes(symbols)


    def get_quote(self, symbol):
        return self.rakuten_client.get_quote(symbol)


    def get_market_des(self, symbol):
        return self.rakuten_client.get_market_des(symbol)


    def remove_quote_symbol(self, symbol):
        self.rakuten_client.remove_quote_symbol(symbol)


    # ==========================================
    # 発注依頼
    #   ・RakutenClientへ注文を依頼する
    #   ・Trade層とはDTOで分離
    # ==========================================
    def request_order(self, request_dto):
         return self.rakuten_client.request_order(request_dto)


    # ==========================================
    # 発注ID一覧データ取得
    #   ・RakutenClientから発注ID一覧シートの1行分データを取得する
    #   ・Trade層とはデータで分離
    # ==========================================
    def get_order_id_data(self, order_id):
        return self.rakuten_client.get_order_id_data(order_id)


    # ==========================================
    # 注文一覧データ取得
    #   ・RakutenClientから注文一覧シートの1行分の生データを取得する
    #   ・Trade層とはデータで分離
    # ==========================================
    def get_order_list_data(self, order_no):
        return self.rakuten_client.get_order_list_data(order_no)


    # ==========================================
    # 注文番号取得
    #   ・RakutenClientから注文番号を取得する
    #   ・Trade層とはDTOで分離
    # ==========================================
    def get_order_no(self, order_id):

        order_no, order_result = self.rakuten_client.get_order_no(order_id)

        if order_no is None:
            raise OrderResultError(
                message=order_result,
                code="ORDER_RESULT_ERROR",
                data={
                    "order_id": order_id,
                },
            )

        return order_no


    # ==========================================
    # 注文結果取得
    # ==========================================
    def get_order_result(self, order_no):
        return self.rakuten_client.get_order_result(order_no)


    # ==========================================
    # 約定結果取得
    #
    #   ・ExecutionListから約定データを取得
    #   ・複数約定を集約
    #   ・Trade層には集約済みデータを返す
    #
    #   約定数量:
    #       各約定の約定数量を合計
    #
    #   約定代金:
    #       各約定の約定代金を合計
    #
    #   約定単価:
    #       約定代金合計 ÷ 約定数量合計
    #
    #       ※単純な約定単価の平均ではなく、
    #         約定数量を考慮した加重平均となる
    #
    # ==========================================
    def get_filled_result(
        self,
        order_datetime,
        symbol,
        account_type,
        margin_type,
        repayment_period,
        trade_type,
        order_type,
    ):
        """
        order_datetime: OrderListから取得した発注/受注日時
        symbol: 銘柄コード
        account_type: 口座区分
        margin_type: 信用区分
        repayment_period: 弁済期限
        trade_type(取引): 現物 / 信用新規 / 信用返済
        order_type(売買): 買付 / 買建 / 買埋 / 売付 / 売建 / 売埋
        """

        results = self.rakuten_client.get_execution_results(
            order_datetime=order_datetime,
            symbol=symbol,
            account_type=account_type,
            margin_type=margin_type,
            repayment_period=repayment_period,
            trade_type=trade_type,
            order_type=order_type,
        )

        if not results:
            return None

        # 約定数量を合計
        quantity = sum(
            result["quantity"]
            for result in results
        )

        # 約定代金を合計
        amount = sum(
            result["amount"]
            for result in results
        )

        if quantity <= 0:
            return None

        # 平均約定単価を算出
        # 約定代金合計 ÷ 約定数量合計
        price = amount / quantity

        last_execution_datetime = max(
            result["execution_datetime"]
            for result in results
        )

        # 実約定市場
        execution_market_name = results[0]["execution_market_name"]

        # 実約定単価
        execution_price = results[0]["execution_price"]

        return {
            "execution_datetime": last_execution_datetime,
            "execution_market_name": execution_market_name,
            "execution_price": execution_price,

            "quantity": quantity,
            "price": price,
        }
