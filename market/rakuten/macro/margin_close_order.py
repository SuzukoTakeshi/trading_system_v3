#
# market/rakuten/macro/margin_close_order.py
#
# Rakuten RSS Margin Close Order
#
# 役割:
#   ・信用返済注文
#   ・RssMarginCloseOrder_V 呼出
#
#

from core.logger import Log


class MarginCloseOrder:

    def __init__(self, client):

        self.client = client


    def submit(self, request):
        """
        信用返済注文

        使用RSS:
            RssMarginCloseOrder_V

        request:
            Market Order Request dict
        """

        # ------------------------------------------
        # RssMarginCloseOrder_V 引数
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
        # 13 建日
        # 14 建単価
        # 15 建市場
        # 16 逆指値条件価格
        # 17 逆指値条件区分
        # 18 逆指値価格区分
        # 19 逆指値価格
        # ------------------------------------------

        # 1: 発注ID
        order_id = request["order_id"]

        # 2: 銘柄コード
        symbol = request["symbol"]

        # 3: 売買区分
        #
        # 信用返済:
        #   1：売り返済
        #   3：買い返済
        #
        if request["order_action"] == "sell":
            action = 1
        else:
            action = 3

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
        #
        # 1：制度（6ヶ月）
        # 2：一般（無期限）
        # 3：一般（14日）
        # 4：一般（1日）
        #
        margin_type = request["margin_type"]

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

        # ------------------------------------------
        # 13～15: 返済建玉情報
        # ------------------------------------------

        # 建日
        open_date = request["open_date"]

        # 建単価
        open_price = request["open_price"]

        # 建市場
        # 1：東証
        # 4：JNX
        # 5：JAX
        # 6：Chi-X
        open_market = request["open_market"]

        # ------------------------------------------
        # 16～19: 逆指値
        # ------------------------------------------

        trigger_price = ""
        trigger_type = ""
        trigger_price_type = ""
        trigger_order_price = ""

        # ------------------------------------------
        # RSS実行
        # ------------------------------------------

        order_result = self.client.run_macro(
            "RssMarginCloseOrder_V",
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
            open_date,
            open_price,
            open_market,
            trigger_price,
            trigger_type,
            trigger_price_type,
            trigger_order_price,
        )

        Log.debug(
            f"RssMarginCloseOrder_V RESULT "
            f"(@{order_id}) "
            f"symbol={symbol} "
            f"margin_type={margin_type} "
            f"open_date={open_date} "
            f"open_price={open_price} "
            f"open_market={open_market} "
            f"status={order_result}"
        )

        if order_result == "":
            result = True
        else:
            result = False

        return result, order_result


# 楽天資料より
# |     # | 項目         | 内容                                     |
# | ----: | ------       | -------------------------------------- |
# |     1 | 発注ID       | `order_id`                             |
# |     2 | 発注トリガー  | `0` 待機 / `1` 発注                        |
# |     3 | 銘柄コード    | `7203` など                              |
# |     4 | 売買区分     | `1=売り返済` / `3=買い返済`                    |
# |     5 | 注文区分      | `0=通常`                                 |
# |     6 | SOR区分      | `0=通常` / `1=SOR`                       |
# |     7 | 信用区分      | 1～4                                    |
# |     8 | 注文数量      | 数量                                     |
# |     9 | 価格区分      | `0=成行` / `1=指値`                        |
# |    10 | 注文価格      | 成行なら省略                                 |
# |    11 | 執行条件      | `1=本日中`                                |
# |    12 | 注文期限      | 期限指定時                                  |
# |    13 | 口座区分      | `0=特定` / `1=一般`                        |
# |    14 | 建日         | `YYYYMMDD`                             |
# |    15 | 建単価       | 数値                                     |
# |    16 | 建市場       | `1=東証` / `4=JNX` / `5=JAX` / `6=Chi-X` |
# | 17～20 | 逆指値関連  | 今回は空欄                                  |
