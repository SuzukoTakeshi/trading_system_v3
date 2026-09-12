#
# market/rakuten/macro/margin_open_order.py
#
# Rakuten RSS Margin Order
#
# 役割:
#   ・信用新規注文
#   ・RssMarginOpenOrder_V 呼出
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


class MarginOpenOrder(MacroBase):

    def __init__(self, rakuten_client):
        super().__init__(rakuten_client)

    # ==========================================
    # 信用新規注文
    #
    # 使用RSS:
    #     RssMarginOpenOrder_V
    #
    # request:
    #     Market Order Request dict
    # ==========================================
    def submit(self, request):

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

        # 3: 売買区分 (1:売 / 3:買)
        if request["order_action"] == OrderAction.BUY:
            action = 3
        else:
            action = 1

        # 4: 注文区分 (0:通常注文 / 1:逆指値付注文 / 2:逆指値待機注文)
        order_type = 0

        # 5: SOR区分 (0:通常注文 / 1:SOR注文)
        sor = 1

        # 6: 信用区分 (1:制度（6ヶ月） / 2:一般（無期限） / 3:一般（14日） / 4:一般（1日）)
        margin_type = self.get_margin_type_code(request["margin_type"])

        # 7: 注文数量
        quantity = request["quantity"]

        # 8: 価格区分 (0:成行 / 1:指値)
        if request["order_type"] == OrderType.MARKET:
            price_type = 0
        else:
            price_type = 1

        # 9: 注文価格
        if request["order_type"] == OrderType.MARKET:
            price = ""
        else:
            price = request["price"]

        # 10: 執行条件 (1:本日中 / 2:今週中 / 3:寄付 / 4:引け / 5:期間指定 / 6:大引不成立 / 7:不成)
        condition = 1

        # 11: 注文期限 執行条件が5：期間指定の場合に使用
        expire = ""

        # 12: 口座区分 (0:特定 / 1:一般 / 2:NISA / 3:旧NISA)
        account = 0

        # 13: 逆指値条件価格
        trigger_price = ""

        # 14: 逆指値条件区分 (1:以上 / 2:以下)
        trigger_type = ""

        # 15: 逆指値価格区分 (0:成行 / 1:指値)
        trigger_price_type = ""

        # 16: 逆指値価格
        trigger_order_price = ""

        # 17: セット注文区分 (0:通常（予約しない） / 1:セット注文（予約する）)
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

        if self.rakuten_client.mode == "real":

            # MacroBaseのrun()を呼出し
            result_code, macro_result = self.run(
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

        else:
            result_code = MacroResultCode.SUCCESS
            macro_result = ""

        # 正常
        if result_code == MacroResultCode.SUCCESS:
            RakutenLog.debug(f"信用新規注文: 正常")
            return True, result_code

        # RSSエラー
        RakutenLog.debug(f"信用新規注文: エラー result_code={result_code.value} macro_result={macro_result}")

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
        trigger_price,
        trigger_type,
        trigger_price_type,
        trigger_order_price,
        set_order_type,
        set_order_price_type,
        set_order_price,
        set_order_condition,
        set_order_expire,
    ):

        RakutenLog.debug("RssMarginOpenOrder_V PARAMS")
        RakutenLog.debug(f"  order_id             = {order_id}")
        RakutenLog.debug(f"  symbol               = {symbol}")
        RakutenLog.debug(f"  action               = {action}")
        RakutenLog.debug(f"  order_type           = {order_type}")
        RakutenLog.debug(f"  sor                  = {sor}")
        RakutenLog.debug(f"  margin_type          = {margin_type}")
        RakutenLog.debug(f"  quantity             = {quantity}")
        RakutenLog.debug(f"  price_type           = {price_type}")
        RakutenLog.debug(f"  price                = {price}")
        RakutenLog.debug(f"  condition            = {condition}")
        RakutenLog.debug(f"  expire               = {expire}")
        RakutenLog.debug(f"  account              = {account}")
        RakutenLog.debug(f"  trigger_price        = {trigger_price}")
        RakutenLog.debug(f"  trigger_type         = {trigger_type}")
        RakutenLog.debug(f"  trigger_price_type   = {trigger_price_type}")
        RakutenLog.debug(f"  trigger_order_price  = {trigger_order_price}")
        RakutenLog.debug(f"  set_order_type       = {set_order_type}")
        RakutenLog.debug(f"  set_order_price_type = {set_order_price_type}")
        RakutenLog.debug(f"  set_order_price      = {set_order_price}")
        RakutenLog.debug(f"  set_order_condition  = {set_order_condition}")
        RakutenLog.debug(f"  set_order_expire     = {set_order_expire}")