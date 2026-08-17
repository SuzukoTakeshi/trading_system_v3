#
# market/rakuten/macro/stock_order.py
#
# Rakuten RSS Stock Order
#
# 役割:
#   ・現物注文
#   ・RssStockOrder_V 呼出
#
#

from core.logger import Log


class StockOrder:

    def __init__(self, client):

        self.client = client


    def submit(self, request):
        """
        現物注文

        使用RSS:
            RssStockOrder_V

        request:
            Market Order Request dict
        """

        # ------------------------------------------
        # RssStockOrder_V 引数
        #
        # 1  発注ID
        # 2  銘柄コード
        # 3  売買区分
        # 4  注文区分
        # 5  SOR区分
        # 6  注文数量
        # 7  価格区分
        # 8  注文価格
        # 9  執行条件
        # 10 注文期限
        # 11 口座区分
        # 12 逆指値条件価格
        # 13 逆指値条件区分
        # 14 逆指値価格区分
        # 15 逆指値価格
        # 16 セット注文区分
        # 17 セット注文価格
        # 18 セット注文執行条件
        # 19 セット注文期限
        # ------------------------------------------

        # 1: 発注ID
        order_id = request["order_id"]

        # 2: 銘柄コード
        symbol = request["symbol"]

        # 3: 売買区分
        # 1：売
        # 3：買
        if request["order_action"] == "buy":
            action = 3
        else:
            action = 1

        # 4: 注文区分
        # 0：通常注文
        # 1：逆指値付通常注文
        # 2：逆指値注文
        order_type = 0

        # 5: SOR区分
        # 0：通常注文
        # 1：SOR注文
        sor = 1

        # 6: 注文数量
        quantity = request["quantity"]

        # 7: 価格区分
        # 0：成行
        # 1：指値
        if request["order_type"] == "market":
            price_type = 0
        else:
            price_type = 1

        # 8: 注文価格
        if request["order_type"] == "market":
            price = ""
        else:
            price = request["price"]

        # 9: 執行条件
        # 1：本日中
        condition = 1

        # 10: 注文期限
        expire = ""

        # 11: 口座区分
        # 0：特定
        # 1：一般
        # 2：NISA
        # 3：旧NISA
        account = 0

        # 12: 逆指値条件価格
        trigger_price = ""

        # 13: 逆指値条件区分
        trigger_type = ""

        # 14: 逆指値価格区分
        trigger_price_type = ""

        # 15: 逆指値価格
        trigger_order_price = ""

        # 16: セット注文区分
        set_order_type = ""

        # 17: セット注文価格
        set_order_price = ""

        # 18: セット注文執行条件
        set_order_condition = ""

        # 19: セット注文期限
        set_order_expire = ""

        # ------------------------------------------
        # RSS実行
        # ------------------------------------------

        order_result = self.client.run_macro(
            "RssStockOrder_V",
            order_id,
            symbol,
            action,
            order_type,
            sor,
            quantity,
            price_type,
            price,
            condition,
            expire,
            account,
            trigger_price,
            trigger_type,
            trigger_price_type,
            trigger_order_price,
            set_order_type,
            set_order_price,
            set_order_condition,
            set_order_expire,
        )

        Log.debug(
            f"RssStockOrder_V RESULT "
            f"(@{order_id}) "
            f"symbol={symbol} "
            f"status={order_result}"
        )

        if order_result == "":
            result = True
        else:
            result = False

        return result, order_result