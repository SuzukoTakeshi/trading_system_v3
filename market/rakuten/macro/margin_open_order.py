#
# market/rakuten/macro/margin_open_order.py
#
# Rakuten RSS Margin Order
#
# 役割:
#   ・信用新規注文
#   ・RssMarginOpenOrder_V 呼出
#


from market.rakuten.macro.macro_base import MacroBase


class MarginOpenOrder(MacroBase):

    def __init__(self, client):
        super().__init__(client)


    def submit(self, request):
        """
        信用新規注文

        使用RSS:
            RssMarginOpenOrder_V

        request:
            Market Order Request dict
        """

        # ------------------------------------------
        # RssMarginOpenOrder_V 引数
        #
        # 1  発注ID
        # 2  銘柄コード
        # 3  売買区分
        # 4  注文区分
        # 5  SOR区分
        # 6  信用区分
        # 7  注文数量
        # 8  価格区分
        # 9  注文価格
        # 10 執行条件
        # 11 注文期限
        # 12 口座区分
        # 13 逆指値条件価格
        # 14 逆指値条件区分
        # 15 逆指値価格区分
        # 16 逆指値価格
        # 17 セット注文区分
        # 18 セット注文価格区分
        # 19 セット注文価格
        # 20 セット注文執行条件
        # 21 セット注文期限
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
        # 1：逆指値付注文
        # 2：逆指値待機注文
        order_type = 0

        # 5: SOR区分
        # 0：通常注文
        # 1：SOR注文
        sor = 1

        # 6: 信用区分
        # 1：制度（6ヶ月）
        # 2：一般（無期限）
        # 3：一般（14日）
        # 4：一般（1日）
        margin_type = 4

        # 7: 注文数量
        quantity = request["quantity"]

        # 8: 価格区分
        # 0：成行
        # 1：指値
        if request["order_type"] == "market":
            price_type = 0
        else:
            price_type = 1

        # 9: 注文価格
        if request["order_type"] == "market":
            price = ""
        else:
            price = request["price"]

        # 10: 執行条件
        # 1：本日中
        condition = 1

        # 11: 注文期限
        expire = ""

        # 12: 口座区分
        # 0：特定
        # 1：一般
        # 2：NISA
        # 3：旧NISA
        account = 0

        # 13: 逆指値条件価格
        trigger_price = ""

        # 14: 逆指値条件区分
        trigger_type = ""

        # 15: 逆指値価格区分
        trigger_price_type = ""

        # 16: 逆指値価格
        trigger_order_price = ""

        # 17: セット注文区分
        set_order_type = ""

        # 18: セット注文価格区分
        set_order_price_type = ""

        # 19: セット注文価格
        set_order_price = ""

        # 20: セット注文執行条件
        set_order_condition = ""

        # 21: セット注文期限
        set_order_expire = ""

        # ------------------------------------------
        # RSS実行
        # ------------------------------------------

        result, macro_result = self.run(
            order_id, symbol,

            "RssMarginOpenOrder_V",
            order_id,
            symbol,
            action,
            order_type,
            sor,
            margin_type,
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
            set_order_price_type,
            set_order_price,
            set_order_condition,
            set_order_expire,
        )

        #
        # 正常
        #
        if macro_result == "":
            return True, None

        #
        # RSSエラー
        #
        result_code = self.get_result_code(macro_result)

        return False, result_code
