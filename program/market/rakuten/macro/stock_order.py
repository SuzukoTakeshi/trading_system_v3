#
# market/rakuten/macro/stock_order.py
#
# Rakuten RSS Stock Order
#
# 役割:
#   ・現物注文
#   ・RssStockOrder_V 呼出
#
# RESULT:
#   RESULT : (正常)
#            ※正常であってもOrderListの発注結果ではエラーとなる可能性あり。
#               エラー[成行の場合、値幅制限上限までの買付可能額が必要です。
#                   1,093円以内で発注可能な指値を入力してください。]
#   RESULT : 注文ID=345 は既に使用済みです。
#   RESULT : 発注ロック中(発注を行うには発注機能を有効にしてください)
#
#
# 以下のステータスは楽天資料からの抜粋で、確認はされてない。
# |    No | ステータス                      | 意味                   |
# | ----: | ------------------------------ | -------------------    |
# |     1 | `発注ID=xxxx`                  | 既に使用済みの発注ID     |
# |     2 | `待機中`                       | 発注トリガーがFalse      |
# |     3 | `発注ロック中`                  | 発注機能がOFF           |
# |     4 | `接続待ち`                      | サーバ未接続            |
# |     5 | `応答待ち`                      | 電文応答待ち            |
# |     6 | `キャンセル`                    | 注文確認画面でキャンセル |
# |     7 | `発注済み(発注ID=xxxx)`         | 発注済み                |
# |     8 | `引数チェックエラーメッセージ`    | 引数エラー             |
# |     9 | `サーバチェックエラーメッセージ`  | サーバ側エラー          |
#
#
# 注意:
#   Excel編集中は以下のエラーが出た。(test/test_stock_order.py結果)
#       EVENT EXCEL OPEN {'path': 'C:\\StockProjects\\TradingData\\楽天RSS_v3.xlsm'}
#       ERROR
#       AttributeError
#       Excel.Application.Workbooks
#

from market.rakuten.rakuten_log import RakutenLog

from market.rakuten.macro.macro_base import (
    MacroBase,
    MacroResultCode,
)

from market.order_enums import (
    OrderAction,    # 売買方向
    OrderType,      # 注文方式
)


class StockOrder(MacroBase):

    def __init__(self, rakuten_client):
        super().__init__(rakuten_client)

    # ==========================================
    # 現物注文
    #
    #     現物注文
    #
    #     使用RSS:
    #         RssStockOrder_V
    #     request:
    #         Market Order Request dict
    # ==========================================
    def submit(self, request):

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
        if request["order_action"] == OrderAction.BUY:
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
        if request["order_type"] == OrderType.MARKET:
            price_type = 0
        else:
            price_type = 1

        # 8: 注文価格
        if request["order_type"] == OrderType.MARKET:
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
        #
        # 正常パターン
        #   RESULT :
        #
        # マーケットスピードII 発注不可
        #   RESULT : 発注ロック中(発注を行うには発注機能を有効にしてください)
        #
        # 注文ID=345 は既に使用済み
        #   RESULT : 注文ID=345 は既に使用済みです。
        #
        # ------------------------------------------
        self._log_params(
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

        if self.rakuten_client.mode == "real":

            # MacroBaseのrun()を呼出し
            result_code, macro_result = self.run(
                order_id, symbol,

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

        else:
            result_code = MacroResultCode.SUCCESS
            macro_result = ""

        # 正常
        if result_code == MacroResultCode.SUCCESS:
            RakutenLog.debug(f"現物注文: 正常")
            return True, result_code

        # RSSエラー
        RakutenLog.debug(f"現物注文: エラー result_code={result_code.value} macro_result={macro_result}")

        return False, result_code


    def _log_params(
        self,
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
    ):

        RakutenLog.debug("RssStockOrder_V PARAMS")
        RakutenLog.debug(f"  order_id             = {order_id}")
        RakutenLog.debug(f"  symbol               = {symbol}")
        RakutenLog.debug(f"  action               = {action}")
        RakutenLog.debug(f"  order_type           = {order_type}")
        RakutenLog.debug(f"  sor                  = {sor}")
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
        RakutenLog.debug(f"  set_order_price      = {set_order_price}")
        RakutenLog.debug(f"  set_order_condition  = {set_order_condition}")
        RakutenLog.debug(f"  set_order_expire     = {set_order_expire}")
