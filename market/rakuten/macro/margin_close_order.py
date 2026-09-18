#
# market/rakuten/macro/margin_close_order.py
#
# Rakuten RSS Margin Close Order
#
# 役割:
#   ・信用返済注文
#   ・RssMarginCloseOrder_V 呼出
#

from market.rakuten.rakuten_log import RakutenLog

from market.rakuten.macro.macro_base import (
    MacroBase,
    MacroResultCode,
)

from market.order_enums import (
    OrderAction,
    OrderType,
)


class MarginCloseOrder(MacroBase):

    def __init__(self, rakuten_client):
        super().__init__(rakuten_client)

    # ==========================================
    # 信用返済注文
    #
    # 使用RSS:
    #     RssMarginCloseOrder_V
    # request:
    #     Market Order Request dict
    # ==========================================
    def submit(self, request):

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

        # 3: 売買区分 (1：売り返済 / 3：買い返済)
        if request["order_action"] == OrderAction.SELL:
            action = 1
        else:
            action = 3

        # 4: 注文区分 (0：通常注文 / 1：逆指値付注文 / 2：逆指値待機注文)
        order_type = 0

        # 5: SOR区分 (0：通常注文 / 1：SOR注文)
        sor = 1

        # 6: 信用区分 (1：制度（6ヶ月）/2：一般（無期限）/3：一般（14日）/4：一般（1日）)
        margin_type = self.get_margin_type_code(request["margin_type"])

        # 7: 注文数量
        quantity = request["quantity"]

        # 8: 価格区分 (0：成行 / 1：指値)
        if request["order_type"] == OrderType.MARKET:
            price_type = 0
        else:
            price_type = 1

        # 9: 注文価格 成行の場合は省略
        if request["order_type"] == OrderType.MARKET:
            price = ""
        else:
            price = request["price"]

        # 10: 執行条件 (1：本日中 / 2：今週中 / 3：寄付 / 4：引け / 5：期間指定 / 6：大引不成立 / 7：不成)
        condition = 1

        # 11: 注文期限 執行条件が5：期間指定の場合に使用
        expire = ""

        # 12: 口座区分 (0：特定 / 1：一般 / 2：NISA / 3：旧NISA)
        account = 0

        # ------------------------------------------
        # 返済建玉情報
        # ------------------------------------------

        # 13: 建日 1建玉と完全に一致している必要があり (YYYYMMDD)
        position_date = request["position_date"]
        # 14: 建単価 1建玉と完全に一致している必要があり
        position_price = request["position_price"]
        # 15: 建市場 1建玉と完全に一致している必要があり (1：東証 / 4：JNX / 5：JAX / 6：Chi-X)
        position_market = request["position_market"]

        # ------------------------------------------
        # 逆指値
        # ------------------------------------------

        # 16: 逆指値条件価格
        trigger_price = ""
        # 17: 逆指値条件区分 (1：以上 / 2：以下)
        trigger_type = ""
        # 18: 逆指値価格区分 (0：成行 / 1：指値)
        trigger_price_type = ""
        # 19: 逆指値価格
        trigger_order_price = ""

        # ------------------------------------------
        # RSS実行
        # ------------------------------------------
        self._log_params(
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
            position_date,
            position_price,
            position_market,
            trigger_price,
            trigger_type,
            trigger_price_type,
            trigger_order_price,
        )

        if self.rakuten_client.mode == "real":

            # MacroBaseのrun()を呼出し
            result_code, macro_result = self.run(
                order_id, symbol,

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
                position_date,
                position_price,
                position_market,
                trigger_price,
                trigger_type,
                trigger_price_type,
                trigger_order_price,
            )

        else:
            result_code = MacroResultCode.SUCCESS
            macro_result = ""

        # 正常
        if result_code == MacroResultCode.SUCCESS:
            RakutenLog.debug(f"信用返済注文: 正常")
            return True, result_code

        # RSSエラー
        RakutenLog.debug(f"信用返済注文: エラー result_code={result_code.value} macro_result={macro_result}")

        return False, result_code


    def _log_params(
        self,
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
        position_date,
        position_price,
        position_market,
        trigger_price,
        trigger_type,
        trigger_price_type,
        trigger_order_price,
    ):

        RakutenLog.debug("RssMarginCloseOrder_V PARAMS")
        RakutenLog.debug(f"  order_id            = {order_id}")
        RakutenLog.debug(f"  symbol              = {symbol}")
        RakutenLog.debug(f"  action              = {action}")
        RakutenLog.debug(f"  order_type          = {order_type}")
        RakutenLog.debug(f"  sor                 = {sor}")
        RakutenLog.debug(f"  margin_type         = {margin_type}")
        RakutenLog.debug(f"  quantity            = {quantity}")
        RakutenLog.debug(f"  price_type          = {price_type}")
        RakutenLog.debug(f"  price               = {price}")
        RakutenLog.debug(f"  condition           = {condition}")
        RakutenLog.debug(f"  expire              = {expire}")
        RakutenLog.debug(f"  account             = {account}")
        RakutenLog.debug(f"  position_date       = {position_date}")
        RakutenLog.debug(f"  position_price      = {position_price}")
        RakutenLog.debug(f"  position_market     = {position_market}")
        RakutenLog.debug(f"  trigger_price       = {trigger_price}")
        RakutenLog.debug(f"  trigger_type        = {trigger_type}")
        RakutenLog.debug(f"  trigger_price_type  = {trigger_price_type}")
        RakutenLog.debug(f"  trigger_order_price = {trigger_order_price}")


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
