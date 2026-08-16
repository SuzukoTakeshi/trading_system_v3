#
# market/rakuten/order_sheet.py
#
# Rakuten RSS Order Sheet
#
# 役割:
#   ・ORDERシート操作
#   ・発注情報書込
#
#

from datetime import datetime

from core.logger import Log

from market.rakuten.sheets.base_sheet import BaseSheet


class OrderSheet(BaseSheet):

    ORDER_ID_COLUMN = "OrderID"
    SYMBOL_COLUMN = "銘柄コード"
    ACTION_COLUMN = "売買（買/売）"
    QUANTITY_COLUMN = "数量"
    STATE_COLUMN = "状態"
    PRICE_COLUMN = "価格（指値）"
    TIME_COLUMN = "時刻"


    def __init__(self, client, ws, mode):

        super().__init__(
            client,
            ws,
            mode=mode,
            header_row=1,
            stopper=None,
        )


    def request_order(self, request):
        """
        発注情報書込
        
        request:
            Market Order Request dict

            order_action:
                buy / sell

            order_type:
                market / limit
        """

        row = self.find_empty_row(self.column_map[self.ORDER_ID_COLUMN])

        self.ws.Cells(row, self.column_map[self.ORDER_ID_COLUMN]).Value = request["order_id"]

        self.ws.Cells(row, self.column_map[self.SYMBOL_COLUMN]).Value = request["symbol"]

        self.ws.Cells(row, self.column_map[self.ACTION_COLUMN]).Value = request["order_action"]

        self.ws.Cells(row, self.column_map[self.QUANTITY_COLUMN]).Value = request["quantity"]

        if request["order_type"] == "market":
            display_price = "成行"
        else:
            display_price = request["price"]
        self.ws.Cells(row, self.column_map[self.PRICE_COLUMN]).Value = display_price

        self.ws.Cells(row, self.column_map[self.STATE_COLUMN]).Value = "REQUEST"

        self.ws.Cells(row, self.column_map[self.TIME_COLUMN]).Value = datetime.now()

        # 調査用
        Log.debug(f"ORDER SHEET : {self.get_row_log(row)}")

        if self.is_real():
            result, rss_result = self._submit_real(request)

        elif self.is_simulator():
            result, rss_result = self._submit_simulator(request)

        elif self.is_emulator():
            result, rss_result = self._submit_emulator(request)


        elif self.is_debug():

            if self.client.debug_settings.get("order_enabled", False):
                result, rss_result = self._submit_real(request)
            else:
                result, rss_result = self._submit_debug(request)

        else:
            raise Exception(f"未対応mode: {self.mode}")

        if result:
            Log.event(f"ORDER REQUEST OK (@{request["order_id"]} "
                f"symbol={request["symbol"]} mode{self.mode}"
            )
        else:
            Log.event(f"ORDER REQUEST NG (@{request["order_id"]} "
                f"rss_result={rss_result} "
                f"symbol={request["symbol"]} mode{self.mode}"
            )

        return result, rss_result


    def _submit_real(self, request):
        """
        楽天RSS発注
        """
        # ------------------------------------------
        # RssStockOrder_V 引数
        # 参考) MARKETSPEEDII RSSオンラインヘルプ
        #   https://marketspeed.jp/ms2_rss/onlinehelp/ohm_002/ohm_002_06.html
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

        # 1:発注ID
        order_id = request["order_id"]

        # 2:銘柄コード
        symbol = request["symbol"]

        # 3:売買区分 (1：売 (売建) 3：買 (買建))
        if request["order_action"] == "buy":
            action = 3
        else:
            action = 1

        # 4: 注文区分 (0：通常注文 1：逆指値付通常注文 2：逆指値注文)
        trade_type = 0

        # 5: SOR区分 (0：通常注文 1：SOR注文)
        sor = 1

        # 6: 注文数量
        quantity = request["quantity"]

        # 7: 価格区分（0：成行 1：指値）「0：通常注文」、「1：逆指値付通常注文」の時必須。
        if request["order_type"] == "market":
            price_type = 0
        else:
            price_type = 1

        # 8: 注文価格
        #  「0：通常注文」、「1：逆指値付通常注文」の時必須。
        #  価格区分が「1：指値」の時必須。成行の場合は省略
        if request["order_type"] == "market":
            price = ""
        else:
            price = request["price"]

        # 9: 執行条件
        # (1：本日中 2：今週中 3：寄付 4：引け 5：期間指定 6：大引不成 7：不成)
        # SOR区分が「1：SOR注文」時、3：寄付　4：引けの選択は不可
        condition = 1

        # 10: 注文期限 (YYYYMMDD) 執行条件が「5：期間指定」の場合のみ必須。それ以外は省略
        expire = ""

        # 11: 口座区分 (0：特定 1：一般 2：NISA 3：旧NISA)
        account = 0

        # 12: 逆指値条件価格 「1：逆指値付通常注文」、「２：逆指値注文」の時必須。
        trigger_price = ""

        # 13: 逆指値条件区分 (0：成行 1：指値) 「1：逆指値付通常注文」、「２：逆指値注文」の時必須。
        trigger_type = ""

        # 14: 逆指値価格区分 (0：成行 1：指値) 「1：逆指値付通常注文」、「２：逆指値注文」の時必須。
        trigger_price_type = ""

        # 15: 逆指値価格 逆指値価格区分が成行の場合は省略
        #   「1：逆指値付通常注文」、「２：逆指値注文」の時必須。
        trigger_order_price = ""

        # 16: セット注文区分 (0：通常（予約しない) 1：セット注文(予約する) 未入力の場合は、通常(予約しない)と同意)
        set_order_type = ""

        # 17: セット注文価格 セット注文区分が「1：セット注文（予約する）」の時必須、それ以外は省略。
        set_order_price = ""

        # 18: セット注文執行条件
        #   (1：本日中 2：今週中 3：寄付 4：引け 5：期間指定 6：大引不成 7：不成
        #   セット注文区分が「1：セット注文（予約する）」の時必須、それ以外は省略
        #   SOR区分が「1：SOR注文」時、3：寄付　4：引けの選択は不可)
        set_order_condition = ""

        # 19: セット注文期限 (YYYYMMDD) セット注文執行条件が「5：期間指定」の場合のみ必須。それ以外は省略
        set_order_expire = ""

        order_result = self.client.run_macro(
            "RssStockOrder_V",
            order_id,            #  1 発注ID
            symbol,              #  2 銘柄コード
            action,              #  3 売買区分
            trade_type,          #  4 注文区分
            sor,                 #  5 SOR区分
            quantity,            #  6 注文数量
            price_type,          #  7 価格区分
            price,               #  8 注文価格
            condition,           #  9 執行条件
            expire,              # 10 注文期限
            account,             # 11 口座区分
            trigger_price,       # 12 逆指値条件価格
            trigger_type,        # 13 逆指値条件区分
            trigger_price_type,  # 14 逆指値価格区分
            trigger_order_price, # 15 逆指値価格
            set_order_type,      # 16 セット注文区分
            set_order_price,     # 17 セット注文価格
            set_order_condition, # 18 セット注文執行条件
            set_order_expire,    # 19 セット注文期限
        )

        Log.debug(f"RssStockOrder_V RESULT (@{order_id}) symbol={symbol} status={order_result}")

        # マーケットスピードII 発注不可
        # order_result : 発注ロック中(発注を行うには発注機能を有効にしてください)
        #
        # 注文ID=345 は既に使用済み
        # order_result : 注文ID=345 は既に使用済みです。
        #
        # order_result : 手数料ゼロコースでは、SORを有効にして、再度注文してください。
        #
        # 正常パターン
        # order_result :

        if order_result == "":
            result = True
        else:
            result = False

        return result, order_result


    def _submit_simulator(self, request):
        return True, ""

    def _submit_emulator(self, request):
        return True, ""

    def _submit_debug(self, request):
        return True, ""
        # エラー確認用
        # return False, "_submit_debug return=False"
